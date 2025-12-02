from difflib import SequenceMatcher
import re

"Detects and removes duplicate/similar questions"
"""
Args:
    similarity_threshold: 0.0: No duplication - 1.0: Definiately duplication.
                      Ex: 0.85 means 85% similar = considered duplicate.
    threshold value: 0.85
"""
class Deduplicator:  
    def __init__(self, similarity_threshold=0.85):
        self.similarity_threshold = similarity_threshold
        self.processed_questions = []
    
    "Normalize text for comparison (lowercase, remove special chars)"
    def _normalize_text(self, text):
        text = text.lower()
        return text
    
    """
    Calculate similarity between two texts (0.0-1.0)
    Using SequenceMatcher from difflib
    """
    def _calculate_similarity(self, text1, text2):
       
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        
        matcher = SequenceMatcher(None, norm1, norm2)
        return matcher.ratio()
    
    "Check if new_question is duplicate of any processed question"
    """
    Args:
        new_question: The new question text
    
    Returns:
        Tuple: (is_duplicate, most_similar_question, similarity_score)
    """
    def is_duplicate(self, new_question):
        for existing_q in self.processed_questions:
            similarity = self._calculate_similarity(new_question, existing_q)
            if similarity >= self.similarity_threshold:
                return True, existing_q, similarity
        
        return False, None, 0.0
    
    "Add a question to tracking list"
    def add_question(self, question_text):
        self.processed_questions.append(question_text)
    
    "Find duplicates within a batch of questions"
    """
    Args:
        questions_list: List of question texts
    
    Returns:
        List of tuples: (question_index, duplicate_index, similarity_score)
    """
    def get_duplicates_in_batch(self, questions_list):
        duplicates = []
        for i, q1 in enumerate(questions_list):
            for j, q2 in enumerate(questions_list):
                if i < j:
                    similarity = self._calculate_similarity(q1, q2)
                    if similarity >= self.similarity_threshold:
                        duplicates.append((i, j, similarity))
        
        return duplicates
    
    "Remove duplicates from a batch, keeping first occurrence"
    """
    Args:
        questions_with_metadata: List of question dicts with 'question' key.
    
    Returns:
        Filtered list with duplicates removed
    """
    def filter_duplicates_in_batch(self, questions_with_metadata):
        filtered = []
        seen_questions = []
        
        for q_dict in questions_with_metadata:
            question_text = q_dict.get('question', '')
            
            is_dup, _, _ = self.is_duplicate(question_text)
            
            if not is_dup:
                filtered.append(q_dict)
                seen_questions.append(question_text)
        
        return filtered
