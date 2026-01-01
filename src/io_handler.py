import json
import os
from src.utils import log_debug

# Handles JSON input/output and validation
class IOHandler:
    
    # Parse JSON input
    """
    Returns:
        Tuple: (parsed_dict, error_message)
    """
    @staticmethod
    def read_json_input(input_text):
        
        try:
            data = json.loads(input_text)
            return data, None
        except json.JSONDecodeError as e:
            error = f"Invalid JSON: {str(e)}"
            log_debug(f"ERROR: {error}")
            return None, error
    
    # Validate question generation request
    """
    Returns:
        Tuple: (is_valid, error_message)
    """
    @staticmethod
    def validate_generation_request(request):
        if not isinstance(request, dict):
            return False, "Request must be a JSON object"
        
        # Check required fields
        if 'element_file' not in request:
            return False, "Missing required field: 'element_file'"
        
        if 'number_of_questions' not in request:
            return False, "Missing required field: 'number_of_questions'"
        
        # Validate element_file
        element_file = request['element_file']
        if not isinstance(element_file, str):
            return False, "'element_file' must be a string"
        
        if not os.path.exists(element_file):
            return False, f"Element file not found: {element_file}"
        
        # Validate number_of_questions
        try:
            num_questions = int(request['number_of_questions'])
            if num_questions < 1:
                return False, "'number_of_questions' must be at least 1"
            if num_questions > 50:
                return False, "'number_of_questions' must not exceed 50"
        except (ValueError, TypeError):
            return False, "'number_of_questions' must be an integer"
        
        return True, None
    
    @staticmethod
    def create_success_response(request, questions, summary_file):
        return {
            "status": "success",
            "element_file": request['element_file'],
            "questions_generated": len(questions),
            "questions": questions,
            "summary_file": summary_file
        }
    
    @staticmethod
    def create_error_response(error_message, debug_message=None):
        response = {
            "status": "error",
            "error_message": error_message
        }
        if debug_message:
            response["debug_message"] = debug_message
        return response
    
    @staticmethod
    def output_json(data):
        print(json.dumps(data, ensure_ascii=False, indent=2))
