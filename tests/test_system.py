import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import json
import subprocess
from src.utils import load_config, round_number, get_timestamp
from src.fact_extractor import FactExtractor
from src.facts_loader import FactsLoader
from src.question_templates import get_all_templates, generate_question_text
from src.deduplicator import Deduplicator
from src.llm_client import OllamaClient
from src.question_generator import QuestionGenerator
from src.summary_generator import SummaryGenerator
from src.io_handler import IOHandler

"""
Comprehensive test suite for Chemistry AI Question Generator
Run: python3 tests/test_system.py
"""

class TestSuite:    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def print_header(self, text):
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_test(self, name, passed, details=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        print(f"{status}: {name}")
        if details:
            print(f"       {details}")
    
    def run_all_tests(self):
        self.print_header("Chemistry AI Question Generator - Test Suite")
        
        self.test_utils()
        self.test_fact_extractor()
        self.test_facts_loader()
        self.test_question_templates()
        self.test_deduplicator()
        self.test_llm_client()
        self.test_question_generator()
        self.test_summary_generator()
        self.test_io_handler()
        self.test_main_integration()
        
        self.print_summary()
    
    "Test modules"
    def test_utils(self):
        self.print_header("Module: utils.py")
        
        # Test round_number
        tests = [
            (137.3, "137"),
            (137.5, "137.5"),
            (137.7, "138"),
        ]
        for value, expected in tests:
            result = round_number(value)
            self.print_test(f"round_number({value})", result == expected, f"Got {result}")
        
        # Test get_timestamp
        ts = get_timestamp()
        self.print_test("get_timestamp()", len(ts) >= 14, f"Format: {ts}")
        
        # Test load_config
        try:
            config = load_config()
            self.print_test("load_config()", 'system' in config, f"Keys: {len(config)}")
        except Exception as e:
            self.print_test("load_config()", False, str(e))
    
    def test_fact_extractor(self):
        self.print_header("Module: fact_extractor.py")
        
        try:
            extractor = FactExtractor()
            result = extractor.extract_from_file('data/chemistry_files/Bari.txt')
            
            self.print_test("extract_from_file()", result is not None, f"Extracted {result['vietnamese_name']}")
            self.print_test("Extract Vietnamese name", result['vietnamese_name'] == "Bari", f"Got {result['vietnamese_name']}")
            self.print_test("Extract facts", len(result['facts']) > 0, f"Facts: {len(result['facts'])}")
        except Exception as e:
            self.print_test("FactExtractor", False, str(e))
    
    def test_facts_loader(self):
        self.print_header("Module: facts_loader.py")
        
        try:
            loader = FactsLoader('data/facts_database/chemistry_facts.csv')
            
            self.print_test("FactsLoader init", loader.df is not None, f"Rows: {len(loader.df)}")
            
            distractors = loader.get_distractors("Nhóm IIA", "Periodic Group", 3)
            self.print_test("get_distractors()", len(distractors) == 3, f"Got {len(distractors)} options")
            
            valid = "Nhóm IIA" not in distractors
            self.print_test("Distractor validity", valid, "Correct answer not in distractors")
        except Exception as e:
            self.print_test("FactsLoader", False, str(e))
    
    def test_question_templates(self):
        self.print_header("Module: question_templates.py")
        
        try:
            templates = get_all_templates()
            self.print_test("get_all_templates()", len(templates) == 8, f"Templates: {len(templates)}")
            
            question = generate_question_text("Periodic Group", "Bari")
            has_element = "Bari" in question
            self.print_test("generate_question_text()", has_element, f"Q: {question[:50]}...")
        except Exception as e:
            self.print_test("QuestionTemplates", False, str(e))
    
    def test_deduplicator(self):
        self.print_header("Module: deduplicator.py")
        
        try:
            dedup = Deduplicator(0.85)
            
            q1 = "Bari thuộc nhóm nào?"
            q2 = "Bari ở nhóm nào?"
            q3 = "Carbon có màu gì?"
            
            sim12 = dedup._calculate_similarity(q1, q2)
            sim13 = dedup._calculate_similarity(q1, q3)
            
            self.print_test("Similarity (similar)", sim12 > 0.7, f"Score: {sim12:.2f}")
            self.print_test("Similarity (different)", sim13 < 0.5, f"Score: {sim13:.2f}")
            
            dedup.add_question(q1)
            is_dup, _, _ = dedup.is_duplicate(q2)
            self.print_test("Duplicate detection", is_dup, "Correctly detected duplicate")
        except Exception as e:
            self.print_test("Deduplicator", False, str(e))
    
    def test_llm_client(self):
        self.print_header("Module: llm_client.py")
        
        try:
            client = OllamaClient()
            
            self.print_test("OllamaClient init", client is not None, f"Model: {client.model_name}")
            self.print_test("is_available() method", callable(client.is_available), "Method exists")
            self.print_test("generate() method", callable(client.generate), "Method exists")
            self.print_test("enhance_question() method", callable(client.enhance_question), "Method exists")
        except Exception as e:
            self.print_test("OllamaClient", False, str(e))
    
    def test_question_generator(self):
        self.print_header("Module: question_generator.py")
        
        try:
            config = load_config()
            qg = QuestionGenerator(config)
            
            self.print_test("QuestionGenerator init", qg is not None, "Initialized")
            
            q = qg._generate_single_question("Bari", {"Period": "6", "Periodic Group": "Nhóm IIA"})
            self.print_test("Generate single question", q is not None, f"Q: {q['question'][:40]}...")
            
            questions = qg.generate_questions('data/chemistry_files/Bari.txt', 2)
            self.print_test("Generate batch (2 questions)", len(questions) == 2, f"Generated: {len(questions)}")
            
            stats = qg.get_statistics()
            self.print_test("Get statistics", 'success_rate' in stats, f"Rate: {stats['success_rate']}")
        except Exception as e:
            self.print_test("QuestionGenerator", False, str(e))
    
    def test_summary_generator(self):
        self.print_header("Module: summary_generator.py")
        
        try:
            gen = SummaryGenerator()
            
            stats = {
                'total_attempts': 10,
                'successful_generations': 3,
                'failed_generations': 1,
                'duplicates_found': 1,
                'llm_enhancements_applied': 2,
                'llm_enhancement_failures': 0,
                'success_rate': '30%'
            }
            
            summary = gen.generate_summary('test.txt', 3, stats, True)
            self.print_test("Generate summary", summary is not None, f"Confidence: {summary['debug_info']['confidence_score']:.2f}")
            
            self.print_test("Summary structure", 'metadata' in summary and 'performance' in summary, "Has required sections")
        except Exception as e:
            self.print_test("SummaryGenerator", False, str(e))
    
    def test_io_handler(self):
        self.print_header("Module: io_handler.py")
        
        try:
            handler = IOHandler()
            
            valid_json = '{"element_file": "test.txt", "number_of_questions": 5}'
            data, error = handler.read_json_input(valid_json)
            self.print_test("read_json_input()", error is None, "Parsed successfully")
            
            request = {"element_file": "data/chemistry_files/Bari.txt", "number_of_questions": 3}
            is_valid, error = handler.validate_generation_request(request)
            self.print_test("validate_generation_request()", is_valid, "Request is valid")
        except Exception as e:
            self.print_test("IOHandler", False, str(e))
    
    def test_main_integration(self):
        self.print_header("Integration: main.py End-to-End")
        
        try:
            request = {
                "element_file": "data/chemistry_files/Bari.txt",
                "number_of_questions": 2
            }
            
            process = subprocess.Popen(
                ['python3', 'main.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=json.dumps(request))
            response = json.loads(stdout)
            
            is_success = response['status'] == 'success'
            self.print_test("main.py generates questions", is_success, f"Status: {response['status']}")
            
            if is_success:
                has_questions = len(response['questions']) > 0
                self.print_test("Questions have required fields", has_questions, f"Q count: {response['questions_generated']}")
                
                if has_questions:
                    q = response['questions'][0]
                    has_fields = all(k in q for k in ['question', 'answer', 'choice1', 'choice2', 'choice3', 'choice4'])
                    self.print_test("Question format valid", has_fields, "All fields present")
        except Exception as e:
            self.print_test("main.py integration", False, str(e))
    
    "Print test summary"
    def print_summary(self):
        self.print_header("Test Summary")
        print(f"\nTotal Tests Run:    {self.tests_run}")
        print(f"Tests Passed:       {self.tests_passed} ✓")
        print(f"Tests Failed:       {self.tests_failed} ✗")
        
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Pass Rate:          {pass_rate:.1f}%")
        
        print("\n" + "=" * 60)
        if self.tests_failed == 0:
            print("  ✓ ALL TESTS PASSED - System is ready!")
        else:
            print(f"  ✗ {self.tests_failed} test(s) failed - Review above")
        print("=" * 60 + "\n")

def main():
    suite = TestSuite()
    suite.run_all_tests()

if __name__ == "__main__":
    main()
