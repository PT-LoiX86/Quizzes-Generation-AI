import json
import os
from datetime import datetime
import re

# Load configuration from config.json
def load_config(config_path="config/config.json"):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Save data to JSON util
def save_json(data, output_path):
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Load data from JSON file util
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Check if the text is pure numeric
def is_pure_numeric(text):
    if not text:
        return False
    # Allow: 0-9, ., ,, - (negative), and whitespace (optional, maybe trim first)
    clean_text = str(text).strip()
    allowed_chars = set("0123456789.,")
    
    for char in clean_text:
        if char not in allowed_chars:
            return False
            
    # Additional check: Must contain at least one digit
    return any(c.isdigit() for c in clean_text)

# Number rounding util
def round_number(value):
    try:
        num = float(str(value).replace(',', '.'))
        decimal_part = num - int(num)
        
        EPSILON = 1e-9
        
        # X.0 - X.4 (e.g., 0.0 to 0.4999...) -> Round down
        if decimal_part < 0.5 - EPSILON:
            return str(int(num))
        
        # X.5 - X.6 (e.g., 0.5 to 0.5999...) -> Keep .5
        # Range is [0.5, 0.6)
        elif decimal_part >= 0.5 - EPSILON and decimal_part < 0.6 - EPSILON:
            return str(int(num)) + ".5"
        
        # X.6+ -> Round up
        else:
            return str(int(num) + 1)
    except:
        return value

# Get timestamp util
def get_timestamp():
    return datetime.now().strftime("%d%m%Y_%H:%M:%S")

# Extract Vie name from the chemistry file (2nd row)
def extract_vietnamese_name(element_file_path):
    try:
        with open(element_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[:5]:
                if "Tên tiếng Việt:" in line:
                    return line.split(":")[-1].strip()
    except Exception as e:
        print(f"Error extracting Vietnamese name: {e}")
    return None

# Debug logging
def log_debug(message, debug_file="logs/debug.log"):
    os.makedirs(os.path.dirname(debug_file) or '.', exist_ok=True)
    timestamp = datetime.now().strftime("%d%m%Y %H:%M:%S")
    with open(debug_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

# Extract number from string
def extract_number(text):
    text = str(text).strip().replace(',', '.')
    match = re.search(r'-?\d+\.?\d*', text)
    return float(match.group()) if match else None