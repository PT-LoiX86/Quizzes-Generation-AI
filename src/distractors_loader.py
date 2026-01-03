import pandas as pd
import random
import difflib
from src.utils import log_debug, is_pure_numeric

class DistractorsLoader:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path, encoding='utf-8')
        self.column_names = list(self.df.columns)
        log_debug(f"Loaded facts database with {len(self.df)} rows and columns: {self.column_names}")

    def get_distractors(self, correct_answer, category, count=3):
        if category not in self.column_names:
            log_debug(f"WARNING: Category '{category}' not found in facts database")
            return []

        all_values = self.df[category].dropna().unique().tolist()
        candidates = []
        
        # Helper to normalize for comparison
        def normalize_for_comparison(val):
            if is_pure_numeric(val):
                try:
                    f = float(str(val).replace(',', '.'))
                    if f.is_integer():
                        return str(int(f))
                    return str(f)
                except:
                    pass
            return str(val).strip().lower()

        norm_target = normalize_for_comparison(correct_answer)
        
        for v in all_values:
            norm_val = normalize_for_comparison(v)
            if norm_val != norm_target:
                candidates.append(v)

        selected_distractors = []
        is_numeric_mode = is_pure_numeric(correct_answer)
        
        if is_numeric_mode:
            selected_distractors = self._get_numeric_distractors(correct_answer, candidates, count)
        else:
            selected_distractors = self._get_string_distractors(correct_answer, candidates, count)
            
        # Fallback
        if len(selected_distractors) < count:
            log_debug(f"WARNING: Only {len(candidates)} distractors available for {category}")
            remaining = [c for c in candidates if c not in selected_distractors]
            needed = count - len(selected_distractors)
            if len(remaining) >= needed:
                selected_distractors.extend(random.sample(remaining, needed))
        
        if is_numeric_mode:
            selected_distractors = [self._format_if_integer(x) for x in selected_distractors]
            
        random.shuffle(selected_distractors)
        return selected_distractors

    def _format_if_integer(self, val):
        try:
            s_val = str(val).replace(',', '.')
            f_val = float(s_val)
            if abs(f_val - round(f_val)) < 1e-9:
                return str(int(round(f_val)))
            return str(val)
        except:
            return str(val)

    def _get_numeric_distractors(self, target, candidates, count):
        try:
            target_val = float(str(target).replace(',', '.'))
            candidate_diffs = []
            for c in candidates:
                if is_pure_numeric(c):
                    c_val = float(str(c).replace(',', '.'))
                    diff = abs(target_val - c_val)
                    candidate_diffs.append((c, diff))
            
            candidate_diffs.sort(key=lambda x: x[1])
            
            return [item[0] for item in candidate_diffs[:count]]
            
        except Exception as e:
            log_debug(f"Error in numeric distractor logic: {e}")
            return random.sample(candidates, min(len(candidates), count))

    def _get_string_distractors(self, target, candidates, count):
        target_str = str(target).lower()
        candidate_scores = []
        for c in candidates:
            c_str = str(c).lower()
            score = difflib.SequenceMatcher(None, target_str, c_str).ratio()
            candidate_scores.append((c, score))
        
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in candidate_scores[:count]]
    
    def get_all_values_for_category(self, category):
        if category not in self.column_names:
            return []
        return self.df[category].dropna().unique().tolist()
        
    def get_categories(self):
        return self.column_names
