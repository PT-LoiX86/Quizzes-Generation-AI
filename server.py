import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

from src.utils import load_config, log_debug, get_timestamp
from src.question_generator import QuestionGenerator
from src.summary_generator import SummaryGenerator
from src.io_handler import IOHandler

# Initialize App and Config
app = FastAPI(title="Chemistry AI Generator", version="1.0.0")
config = load_config()

# Define Request Model (Validation)
class GenerationRequest(BaseModel):
    element_file: str
    number_of_questions: int

@app.on_event("startup")
async def startup_event():
    log_debug("=" * 50)
    log_debug(f"API Server Started - {get_timestamp()}")
    log_debug("=" * 50)

@app.post("/api/generate", response_model=Dict[str, Any])
async def generate_questions_endpoint(req: GenerationRequest):
    
    # Endpoint to generate chemistry questions.
    try:
        # Convert Pydantic model to dict for compatibility with your existing code
        request_data = req.dict()
        
        log_debug(f"API Request received: {request_data}")
        
        # Get element path from config
        elements_base_path = config['data_paths']['chemistry_files']
        
        # Validate request & Resolve Path
        is_valid, error_msg, full_element_path = IOHandler.validate_generation_request(
            request_data, 
            base_path=elements_base_path
        )
        
        if not is_valid:
            log_debug(f"Validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
        # Generation
        log_debug(f"Starting generation for: {full_element_path}")
        qg = QuestionGenerator(config)
        
        questions = qg.generate_questions(
            full_element_path,
            request_data['number_of_questions']
        )
        
        # Summary
        summary_gen = SummaryGenerator()
        summary = summary_gen.generate_summary(
            request_data['element_file'],
            len(questions),
            qg.get_statistics(),
            success=True
        )
        summary_file = summary_gen.save_summary(summary)
        
        # Response
        response = IOHandler.create_success_response(request_data, questions, summary_file)
        
        log_debug(f"SUCCESS: Generated {len(questions)} questions")
        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        log_debug(f"SERVER ERROR: {str(e)}")
        import traceback
        log_debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Health check endpoint for verifying service status
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Chemistry AI Generator"}

if __name__ == "__main__":
    # Run server: python server.py
    # Access at: http://localhost:8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
