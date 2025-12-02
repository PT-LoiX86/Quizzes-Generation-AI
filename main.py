#!/usr/bin/env python3
# main.py

import json
import sys
import os
from src.utils import load_config, log_debug, get_timestamp
from src.question_generator import QuestionGenerator
from src.summary_generator import SummaryGenerator

"Read JSON request from stdin"
"For testing only"
def read_request_from_stdin():
    
    try:
        request_text = sys.stdin.read()
        return json.loads(request_text)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {str(e)}"

"Validate request has required fields"
def validate_request(request):
    if not isinstance(request, dict):
        return False, "Request must be a JSON object"
    
    if 'element_file' not in request:
        return False, "Missing required field: element_file"
    
    if 'number_of_questions' not in request:
        return False, "Missing required field: number_of_questions"
    
    try:
        num_questions = int(request['number_of_questions'])
        if num_questions < 1 or num_questions > 50:
            return False, "number_of_questions must be between 1 and 50"
    except (ValueError, TypeError):
        return False, "number_of_questions must be an integer"
    
    # Check file exists
    element_file = request['element_file']
    if not os.path.exists(element_file):
        return False, f"Element file not found: {element_file}"
    
    return True, None

"Create success response JSON"
def create_success_response(request, questions, summary_file):
    return {
        "status": "success",
        "element_file": request['element_file'],
        "questions_generated": len(questions),
        "questions": questions,
        "summary_file": summary_file
    }

"Create error response JSON"
def create_error_response(error_message, debug_message=None):
    response = {
        "status": "error",
        "error_message": error_message
    }
    if debug_message:
        response["debug_message"] = debug_message
    return response

def main():
    try:
        # Load configuration
        config = load_config()
        log_debug("=" * 50)
        log_debug(f"Chemistry AI Question Generator Started - {get_timestamp()}")
        log_debug("=" * 50)
        
        # Read request from stdin
        request = read_request_from_stdin()
        if request is None:
            error_response = create_error_response(
                "Failed to parse JSON from stdin",
                "Ensure input is valid JSON"
            )
            print(json.dumps(error_response, ensure_ascii=False))
            log_debug(f"ERROR: Invalid JSON input")
            return
        
        log_debug(f"Received request: {request}")
        
        # Validate request
        is_valid, error_msg = validate_request(request)
        if not is_valid:
            error_response = create_error_response(
                error_msg,
                f"Request validation failed for: {json.dumps(request)}"
            )
            print(json.dumps(error_response, ensure_ascii=False))
            log_debug(f"ERROR: {error_msg}")
            return
        
        # Generate questions
        log_debug(f"Starting question generation...")
        qg = QuestionGenerator(config)
        
        questions = qg.generate_questions(
            request['element_file'],
            request['number_of_questions']
        )
        
        # Generate summary
        summary_gen = SummaryGenerator()
        summary = summary_gen.generate_summary(
            request['element_file'],
            len(questions),
            qg.get_statistics(),
            success=True
        )
        
        # Save summary
        summary_file = summary_gen.save_summary(summary)
        log_debug(f"Summary saved: {summary_file}")
        
        # Create response
        response = create_success_response(request, questions, summary_file)
        
        # Output response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        log_debug(f"SUCCESS: Generated {len(questions)} questions")
        log_debug("=" * 50)
        
    except Exception as e:
        error_response = create_error_response(
            str(e),
            f"Unexpected error: {type(e).__name__}"
        )
        print(json.dumps(error_response, ensure_ascii=False))
        log_debug(f"ERROR: {str(e)}")
        import traceback
        log_debug(traceback.format_exc())

if __name__ == "__main__":
    main()
