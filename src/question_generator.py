import random
from src.fact_extractor import FactExtractor
from src.distractors_loader import DistractorsLoader
from src.question_templates import generate_question_text, get_all_templates, get_template
from src.deduplicator import Deduplicator
from src.utils import log_debug

class QuestionGenerator:
    def __init__(self, config):
        self.config = config
        self.fact_extractor = FactExtractor()
        self.facts_loader = DistractorsLoader(config['data_paths']['facts_database'])
        self.deduplicator = Deduplicator(
            similarity_threshold=config['deduplication']['similarity_threshold']
        )
        
        self.statistics = {
            'total_attempts': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'duplicates_found': 0
        }
        
        self.template_weights = self._build_template_weights()
    
    # Main method: Generate questions for an element
    """
    Args:
        element_file: Path to chemistry file
        number_of_questions: Number of questions to generate
    
    Returns:
        List of question dictionaries with 'question', 'answer', 'choice1-4'
    """
    def generate_questions(self, element_file, number_of_questions):
        log_debug(f"Starting generation: {element_file}, {number_of_questions} questions")
        
        extracted = self.fact_extractor.extract_from_file(element_file)
        element_name_vi = extracted['vietnamese_name']
        element_name_en = extracted['english_name']
        
        log_debug(f"Extracted element: {element_name_vi} ({element_name_en})")
        
        questions = []
        attempts = 0
        
        # Track templates that failed for this element so we don't retry them
        failed_templates = set()
        
        # Allow multiple attempts in case of failed generations
        max_attempts = number_of_questions * self.config.get('question_generation', {}).get('max_attempts', 5)
        
        while len(questions) < number_of_questions and attempts < max_attempts:
            # Filter pool to exclude known bad templates
            valid_pool = [t for t in self.template_weights if t not in failed_templates]
            
            if not valid_pool:
                log_debug("No valid templates remaining for this element.")
                break
            
            template_name = random.choice(valid_pool)
            
            attempts += 1
            self.statistics['total_attempts'] += 1
            
            # Try to generate one question
            question_dict = self._generate_single_question(
                element_name_vi,
                extracted['facts'],
                template_name  # Pass template name directly
            )
            
            if question_dict is None:
                # Mark as failed so we don't pick it again for this element
                failed_templates.add(template_name)
                self.statistics['failed_generations'] += 1
                continue
            
            # Check for duplicates
            is_dup, _, _ = self.deduplicator.is_duplicate(question_dict['question'])
            if is_dup:
                self.statistics['duplicates_found'] += 1
                log_debug(f"  ⚠ Duplicate detected, skipping")
                continue
            
            # Add to results
            questions.append(question_dict)
            self.deduplicator.add_question(question_dict['question'])
            self.statistics['successful_generations'] += 1
            
            log_debug(f"Generated question {len(questions)}/{number_of_questions}")
        
        log_debug(f"Generation complete: {len(questions)} questions generated in {attempts} attempts")
        
        return questions
    
    # Generate a single question
    """
    Returns:
        Dictionary with question, answer, choice1-4, or None if failed
    """
    def _generate_single_question(self, element_name, facts, template_name):
        # NOTE: template_name is passed in, logic removed random choice
        
        # Get the specific template
        template_def = get_template(template_name)
        if not template_def: 
            return None
            
        vi_key = template_def.get("category")
        
        # Get answer value from facts using Vietnamese key
        raw_fact = facts.get(vi_key, None)
        if raw_fact is None:
            log_debug(f"  ✗ Template '{template_name}': No answer found for key '{vi_key}'")
            return None
            
        all_correct_answers = []
        if isinstance(raw_fact, list):
            all_correct_answers = [str(x).strip().lower() for x in raw_fact]
            raw_answer = random.choice(raw_fact)
        else:
            all_correct_answers = [str(raw_fact).strip().lower()]
            raw_answer = raw_fact
            
        answer = self._capitalize_first(raw_answer)
        log_debug(f"  ✓ Template '{template_name}': Found answer '{answer}'")
        
        # Generate base question
        question_text = generate_question_text(template_name, element_name)
        
        # Get distractors (wrong answers)
        initial_distractors = self.facts_loader.get_distractors(answer, vi_key, 10)
        log_debug(f"    Got {len(initial_distractors)} candidates from CSV for category '{vi_key}'")
        
        # Validate Distractors
        valid_distractors = []
        for d in initial_distractors:
            # Check if this distractor is actually one of the OTHER correct answers
            d_str = str(d).strip().lower()
            if d_str not in all_correct_answers:
                valid_distractors.append(d)
                
            if len(valid_distractors) >= 3:
                break
        
        if len(valid_distractors) < 3:
            log_debug(f"    WARNING: Only {len(valid_distractors)} valid distractors for {vi_key}")
            # Pad with any available values if needed
            all_values = self.facts_loader.get_all_values_for_category(vi_key)
            for val in all_values:
                val_str = str(val).strip().lower()
                
                # Check against ALL correct answers and existing valid distractors
                if val_str not in all_correct_answers and val not in valid_distractors:
                    valid_distractors.append(val)
                    if len(valid_distractors) >= 3:
                        break
            log_debug(f"    After padding: {len(valid_distractors)} distractors available")
        
        if len(valid_distractors) < 3:
            log_debug(f"    ✗ FAILED: Not enough distractors ({len(valid_distractors)} < 3)")
            return None
        
        # Shuffle all options (correct + distractors)
        formatted_distractors = [self._capitalize_first(d) for d in valid_distractors]
        all_choices = [answer] + formatted_distractors[:3]
        random.shuffle(all_choices)
        
        # Create question dict
        question_dict = {
            'question': question_text,
            'answer': str(answer),
            'choice1': str(all_choices[0]),
            'choice2': str(all_choices[1]),
            'choice3': str(all_choices[2]),
            'choice4': str(all_choices[3]) if len(all_choices) > 3 else str(formatted_distractors[0])
        }
        
        log_debug(f"    ✓ Question generated successfully")
        return question_dict
    
    # Build a list of templates where higher priority items appear more often.
    def _build_template_weights(self):
        weighted_templates = []
        q_types = self.config.get('question_types', {})
        
        # Max priority to calculate inverse weight
        max_p = 5 
        
        all_available_templates = get_all_templates()
        
        for category, settings in q_types.items():
            if not settings.get('enabled', False):
                continue
                
            priority = settings.get('priority', 3)
            weight = max(1, max_p - priority)
            
            # For each specific question type in this category
            for q_type in settings.get('types', []):
                # Only add if it's a valid template we have defined
                if q_type in all_available_templates:
                    weighted_templates.extend([q_type] * weight)
        
        # Fallback if config is empty or invalid
        if not weighted_templates:
            return all_available_templates
            
        return weighted_templates
    
    # Capitalize the first letter of the answer if needed
    def _capitalize_first(self, text):
        if not text:
            return text
        text_str = str(text).strip()
        if not text_str:
            return ""
        
        first_char = text_str[0]
        if first_char.isalpha():
            return first_char.upper() + text_str[1:]
            
        return text_str
    
    def get_statistics(self):
        if self.statistics['total_attempts'] > 0:
            success_rate = (self.statistics['successful_generations'] /
                          self.statistics['total_attempts'] * 100)
        else:
            success_rate = 0.0
        
        return {
            **self.statistics,
            'success_rate': f"{success_rate:.1f}%"
        }
