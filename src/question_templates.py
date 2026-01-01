QUESTION_TEMPLATES = {
    "Period": {
        "Vietnamese": "{element} ở chu kỳ nào trong bảng tuần hoàn?",
        "English": "{element} is in which period of the periodic table?",
        "category": "Period"
    },
    
    "Periodic Group": {
        "Vietnamese": "{element} thuộc nhóm nào trong bảng tuần hoàn?",
        "English": "{element} belongs to which group in the periodic table?",
        "category": "Periodic Group"
    },
    
    "Color": {
        "Vietnamese": "{element} có màu gì?",
        "English": "What color is {element}?",
        "category": "Color"
    },
    
    "Flame Color": {
        "Vietnamese": "Đốt cháy hợp chất của {element}, ngọn lửa có màu gì?",
        "English": "When burning {element} compounds, what color is the flame?",
        "category": "Flame Color"
    },
    
    "Physical State": {
        "Vietnamese": "{element} ở trạng thái vật lý nào ở nhiệt độ phòng?",
        "English": "What is the physical state of {element} at room temperature?",
        "category": "Physical State"
    },
    
    "Element Type": {
        "Vietnamese": "{element} là loại nguyên tố nào?",
        "English": "What type of element is {element}?",
        "category": "Element Type"
    },
    
    "Chemical Character": {
        "Vietnamese": "Tính chất hóa học chủ yếu của {element} là gì?",
        "English": "What is the primary chemical character of {element}?",
        "category": "Chemical Character"
    },
    
    "Valence": {
        "Vietnamese": "Hóa trị chính của {element} là gì?",
        "English": "What is the primary valence of {element}?",
        "category": "Valence"
    }
}

def get_template(template_name):
    return QUESTION_TEMPLATES.get(template_name, None)

def get_all_templates():
    return list(QUESTION_TEMPLATES.keys())

# Generate question text from template
"""
Args:
    template_name: Key from QUESTION_TEMPLATES
    element_name: Vietnamese element name

Returns:
    Vietnamese question text
"""
def generate_question_text(template_name, element_name):
    template = get_template(template_name)
    if not template:
        return None
    
    return template["Vietnamese"].format(element=element_name)
