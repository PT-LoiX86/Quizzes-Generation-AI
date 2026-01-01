import pandas as pd
import random
from src.utils import log_debug

class FactsLoader:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path, encoding='utf-8')
        self.column_names = list(self.df.columns)
        log_debug(f"Loaded facts database with {len(self.df)} rows and columns: {self.column_names}")
    
    # Extract distractors from chemistry facts
    """ 
    Args:
        correct_answer: The correct answer (to exclude).
        category: Column name in CSV (e.g., "Chu kì", "Nhóm").
        count: Number of choices needed (default 3).
    
    Returns:
        List of distractor (different from correct_answer).
    """
    def get_distractors(self, correct_answer, category, count=3):   
        if category not in self.column_names:
            log_debug(f"WARNING: Category '{category}' not found in facts database")
            return []
        
        # Get all values from this column, remove NaN
        all_values = self.df[category].dropna().unique().tolist()
        
        # Remove the correct answer from candidates
        candidates = [v for v in all_values if str(v).strip() != str(correct_answer).strip()]
        
        # If not enough candidates, return what we have
        if len(candidates) < count:
            log_debug(f"WARNING: Only {len(candidates)} distractors available for {category}")
            return candidates
        
        # Randomly select and return
        distractors = random.sample(candidates, count)
        return distractors
    
    # Get all unique values for a category
    def get_all_values_for_category(self, category):
        if category not in self.column_names:
            return []
        return self.df[category].dropna().unique().tolist()
    
    def get_categories(self):
        return self.column_names