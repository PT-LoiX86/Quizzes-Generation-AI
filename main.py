#!/usr/bin/env python3
# main.py

import json
import sys
import os
from src.utils import load_config, log_debug, get_timestamp
from src.question_generator import QuestionGenerator
from src.summary_generator import SummaryGenerator
from src.io_handler import IOHandler

def main():
    try:
        # Load configuration
        config = load_config()
        log_debug("=" * 50)
        log_debug(f"Chemistry AI Question Generator Started - {get_timestamp()}")
        log_debug("=" * 50)
        
        # Read request from stdin using IOHandler
        input_text = sys.stdin.read()
        request, error_msg = IOHandler.read_json_input(input_text)
        
        if request is None:
            error_response = IOHandler.create_error_response(
                "Failed to parse JSON from stdin",
                f"Invalid JSON input: {error_msg}"
            )
            print(json.dumps(error_response, ensure_ascii=False))
            log_debug(f"ERROR: Invalid JSON input - {error_msg}")
            return
        
        log_debug(f"Received request: {request}")
        
        # Get base path for elements from config
        elements_base_path = config['data_paths']['chemistry_files']
        
        # Validate request using IOHandler (handles path resolution)
        is_valid, error_msg, full_element_path = IOHandler.validate_generation_request(
            request, 
            base_path=elements_base_path
        )
        
        if not is_valid:
            error_response = IOHandler.create_error_response(
                error_msg,
                f"Request validation failed"
            )
            print(json.dumps(error_response, ensure_ascii=False))
            log_debug(f"ERROR: {error_msg}")
            return
        
        # Generate questions using the RESOLVED full_element_path
        log_debug(f"Starting question generation for file: {full_element_path}")
        qg = QuestionGenerator(config)
        
        questions = qg.generate_questions(
            full_element_path,
            request['number_of_questions']
        )
        
        # Generate summary
        summary_gen = SummaryGenerator()
        summary = summary_gen.generate_summary(
            request['element_file'], # Use original filename for report
            len(questions),
            qg.get_statistics(),
            success=True
        )
        
        # Save summary
        summary_file = summary_gen.save_summary(summary)
        log_debug(f"Summary saved: {summary_file}")
        
        # Create response
        response = IOHandler.create_success_response(request, questions, summary_file)
        
        # Output response
        IOHandler.output_json(response)
        log_debug(f"SUCCESS: Generated {len(questions)} questions")
        log_debug("=" * 50)
        
    except Exception as e:
        error_response = IOHandler.create_error_response(
            str(e),
            f"Unexpected error: {type(e).__name__}"
        )
        print(json.dumps(error_response, ensure_ascii=False))
        log_debug(f"ERROR: {str(e)}")
        import traceback
        log_debug(traceback.format_exc())

if __name__ == "__main__":
    main()
