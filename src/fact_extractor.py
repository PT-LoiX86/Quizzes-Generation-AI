import re
from src.utils import extract_number, round_number, log_debug, is_pure_numeric

class FactExtractor:
    def __init__(self):
        self.vietnamese_name = None
        self.english_name = None
        self.facts = {}
    
    def extract_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._extract_names(content)
        
        self._extract_structured_facts(content)
        log_debug(f"Extracted {len(self.facts)} structured facts")
        
        return {
            'vietnamese_name': self.vietnamese_name,
            'english_name': self.english_name,
            'facts': self.facts
        }
    
    def _extract_names(self, content):
        lines = content.split('\n')
        for line in lines[:5]:
            if "Tên tiếng Anh:" in line:
                self.english_name = line.split(":")[-1].strip()
            elif "Tên tiếng Việt:" in line:
                self.vietnamese_name = line.split(":")[-1].strip()
    
    def _extract_structured_facts(self, content):
        # Pattern: Key: Value
        pattern = r'^[\s\-]*([^:]+):\s*(.+)$'
        
        for line in content.split('\n'):
            if not line.strip() or line.startswith('I.') or line.startswith('II.') or line.startswith('III.') or line.startswith('IV.') or line.startswith('V.'):
                continue
            
            match = re.match(pattern, line.strip())
            if match:
                key = match.group(1).strip()
                raw_value = match.group(2).strip()
                
                if "Tên tiếng Việt" in key:
                    continue
                
                value = raw_value
                if is_pure_numeric(raw_value):
                    num = extract_number(raw_value)
                    if num is not None:
                        value = round_number(num)
                
                if key in self.facts:
                    existing = self.facts[key]
                    if isinstance(existing, list):
                        self.facts[key].append(value)
                    else:
                        self.facts[key] = [existing, value]
                else:
                    self.facts[key] = value
    
    # Retrieve a specific fact
    """
    Args:
        key: The fact key (e.g., "Nhóm", "Chu kỳ")
        rounded: If True, returns rounded numeric value if the value of the fact is numeric
    """
    def get_fact(self, key, rounded=False):
        lookup_key = f"{key}_rounded" if rounded else key
        return self.facts.get(lookup_key, None)
    
    def get_all_facts(self):
        return self.facts
