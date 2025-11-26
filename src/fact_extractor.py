import re
from src.utils import extract_number, round_number

"Class for chemistry facts extracting from chemistry_facts.csv"
class FactExtractor:
    def __init__(self):
        self.vietnamese_name = None
        self.english_name = None
        self.facts = {}
    
    "Main extracting function"
    def extract_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._extract_names(content)
        self._extract_key_value_pairs(content)
        
        return {
            'vietnamese_name': self.vietnamese_name,
            'english_name': self.english_name,
            'facts': self.facts
        }
    
    "Chemistry names extracting function"
    def _extract_names(self, content):
        lines = content.split('\n')
        for line in lines[:5]:
            if "Tên tiếng Anh:" in line:
                self.english_name = line.split(":")[-1].strip()
            elif "Tên tiếng Việt:" in line:
                self.vietnamese_name = line.split(":")[-1].strip()
    
    "Extract key (fact type) - value (fact) pairs from chemistry data file, like 'Nhóm: IA'"
    def _extract_key_value_pairs(self, content):     
        # Pattern: Key: Value
        pattern = r'^([^:]+):\s*(.+)$'
        
        for line in content.split('\n'):
            # Skip empty lines and section headers
            # IMPORTANT: more section headers defining needed!
            if not line.strip() or line.startswith('I.') or line.startswith('II.'):
                continue
            
            match = re.match(pattern, line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                if "Tên tiếng" in key:
                    continue
                
                # Store original value
                self.facts[key] = value
                
                # Also store rounded version if numeric
                numeric_value = extract_number(value)
                if numeric_value is not None:
                    self.facts[f"{key}_rounded"] = round_number(numeric_value)
    
    """
        Retrieve a specific fact
        
        Args:
            key: The fact key (e.g., "Nhóm", "Chu kỳ")
            rounded: If True, returns rounded numeric value if the value of the fact is numeric
    """
    def get_fact(self, key, rounded=False):
        lookup_key = f"{key}_rounded" if rounded else key
        return self.facts.get(lookup_key, None)
    
    "Return all extracted facts"
    def get_all_facts(self):
        return self.facts
