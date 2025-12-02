import random
from src.fact_extractor import FactExtractor
from src.facts_loader import FactsLoader
from src.question_templates import generate_question_text, get_all_templates
from src.deduplicator import Deduplicator
from src.llm_client import OllamaClient
from src.utils import log_debug, get_timestamp

"Main question generation engine - orchestrates all other modules"
"""
Initialize the generator with configuration

Args:
    config: Configuration dictionary from config.json
"""
class QuestionGenerator:
    
    VI_TO_EN_MAPPING = {
        'Nhóm': 'Periodic Group',
        'Chu kỳ': 'Period',
        'Nguyên tử khối': 'Atomic Mass',
        'Độ âm điện': 'Electronegativity',
        'Cấu hình electron': 'Electron Config',
        'Trạng thái vật lý': 'Physical State',
        'Tính chất hóa học': 'Chemical Character',
        'Hóa trị': 'Valence',
        'Màu sắc': 'Color',
        'Màu lửa': 'Flame Color',
        'Loại nguyên tố': 'Element Type'
    }
    
    def __init__(self, config):
        
        self.config = config
        self.fact_extractor = FactExtractor()
        self.facts_loader = FactsLoader(config['data_paths']['facts_database'])
        self.deduplicator = Deduplicator(
            similarity_threshold=config['deduplication']['similarity_threshold']
        )
        self.llm_client = OllamaClient() if config['ollama']['enabled'] else None
        
        self.statistics = {
            'total_attempts': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'llm_enhancements_applied': 0,
            'llm_enhancement_failures': 0,
            'duplicates_found': 0
        }
    
    """
    Main method: Generate questions for an element
    
    Args:
        element_file: Path to chemistry file
        number_of_questions: Number of questions to generate
    
    Returns:
        List of question dictionaries with 'question', 'answer', 'choice1-4'
    """
    def generate_questions(self, element_file, number_of_questions):
        
        log_debug(f"Starting generation: {element_file}, {number_of_questions} questions")
        
        # Extract element facts
        extracted = self.fact_extractor.extract_from_file(element_file)
        element_name_vi = extracted['vietnamese_name']
        element_name_en = extracted['english_name']
        
        log_debug(f"Extracted element: {element_name_vi} ({element_name_en})")
        
        questions = []
        attempts = 0
        # Allow multiple attempts in case of failed generations
        max_attempts = number_of_questions * 3
        
        while len(questions) < number_of_questions and attempts < max_attempts:
            attempts += 1
            self.statistics['total_attempts'] += 1
            
            # Try to generate one question
            question_dict = self._generate_single_question(
                element_name_vi,
                extracted['facts']
            )
            
            if question_dict is None:
                self.statistics['failed_generations'] += 1
                continue
            
            # Check for duplicates
            is_dup, _, _ = self.deduplicator.is_duplicate(question_dict['question'])
            if is_dup:
                self.statistics['duplicates_found'] += 1
                continue
            
            # Add to results
            questions.append(question_dict)
            self.deduplicator.add_question(question_dict['question'])
            self.statistics['successful_generations'] += 1
            
            log_debug(f"Generated question {len(questions)}/{number_of_questions}")
        
        log_debug(f"Generation complete: {len(questions)} questions generated in {attempts} attempts")
        
        return questions
    
    """
    Generate a single question
    
    Returns:
        Dictionary with question, answer, choice1-4, or None if failed
    """
    def _generate_single_question(self, element_name, facts):
        # Select random template
        templates = get_all_templates()
        template_name = random.choice(templates)
        
        # Get Vietnamese key from template
        vi_key = self._get_category_for_template(template_name)
        
        # Get answer value from facts using Vietnamese key
        answer = facts.get(vi_key, None)
        if answer is None:
            return None
        
        # Generate base question
        base_question = generate_question_text(template_name, element_name)
        
        # Optionally enhance with LLM
        if self.config['question_generation']['use_llm_enhancement'] and self.llm_client:
            enhanced = self.llm_client.enhance_question(base_question)
            if enhanced and len(enhanced) > 5:
                question_text = enhanced
                self.statistics['llm_enhancements_applied'] += 1
            else:
                question_text = base_question
                self.statistics['llm_enhancement_failures'] += 1
        else:
            question_text = base_question
        
        # Convert Vietnamese key to English for CSV lookup
        en_category = self.VI_TO_EN_MAPPING.get(vi_key, vi_key)
        
        # Get distractors (wrong answers)
        distractors = self.facts_loader.get_distractors(answer, en_category, 3)
        
        if len(distractors) < 3:
            log_debug(f"WARNING: Only {len(distractors)} distractors for {en_category}")
            # Pad with any available values if needed
            all_values = self.facts_loader.get_all_values_for_category(en_category)
            for val in all_values:
                if val not in distractors and str(val).strip() != str(answer).strip():
                    distractors.append(val)
                    if len(distractors) >= 3:
                        break
        
        if len(distractors) < 3:
            return None  # Can't generate valid question without enough options
        
        # Shuffle all options (correct + distractors)
        all_choices = [answer] + distractors[:3]
        random.shuffle(all_choices)
        
        # Create question dict
        question_dict = {
            'question': question_text,
            'answer': str(answer),
            'choice1': str(all_choices[0]),
            'choice2': str(all_choices[1]),
            'choice3': str(all_choices[2]),
            'choice4': str(all_choices[3]) if len(all_choices) > 3 else str(distractors[0])
        }
        
        return question_dict
    
    "Map template name to CSV category"
    def _get_category_for_template(self, template_name):
        mapping = {
            "Period": "Chu kỳ",
            "Periodic Group": "Nhóm",
            "Color": "Màu sắc",
            "Flame Color": "Màu lửa",
            "Physical State": "Trạng thái vật lý",
            "Element Type": "Loại nguyên tố",
            "Chemical Character": "Tính chất hóa học",
            "Valence": "Hóa trị"
        }
        return mapping.get(template_name, "Chu kỳ")
    
    "Return generation statistics"
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
