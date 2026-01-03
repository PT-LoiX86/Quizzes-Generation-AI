QUESTION_TEMPLATES = {
    # --- Priority 1: Identification & Periodic Table ---
    "Symbol": {
        "Vietnamese": "Kí hiệu hóa học của {element} là gì?",
        "English": "What is the chemical symbol for {element}?",
        "category": "Kí hiệu"
    },
    "English Name": {
        "Vietnamese": "Tên tiếng Anh của nguyên tố {element} là gì?",
        "English": "What is the English name for element {element}?",
        "category": "Tên tiếng Anh"
    },
    "Period": {
        "Vietnamese": "{element} ở chu kỳ nào trong bảng tuần hoàn?",
        "English": "{element} is in which period of the periodic table?",
        "category": "Chu kỳ"
    },
    "Periodic Group": {
        "Vietnamese": "{element} thuộc nhóm nào trong bảng tuần hoàn?",
        "English": "{element} belongs to which group in the periodic table?",
        "category": "Nhóm"
    },
    "Atomic Mass": {
        "Vietnamese": "Nguyên tử khối của {element} là bao nhiêu?",
        "English": "What is the atomic mass of {element}?",
        "category": "Nguyên tử khối"
    },
    "Element Type": {
        "Vietnamese": "{element} là loại nguyên tố nào?",
        "English": "What type of element is {element}?",
        "category": "Loại nguyên tố "
    },

    # --- Priority 2: Structure & Physical Properties ---
    "Electron Config": {
        "Vietnamese": "Cấu hình electron của {element} là gì?",
        "English": "What is the electron configuration of {element}?",
        "category": "Cấu hình electron"
    },
    "Valence": {
        "Vietnamese": "Hóa trị chính của {element} là gì?",
        "English": "What is the primary valence of {element}?",
        "category": "Hóa trị"
    },
    "Color": {
        "Vietnamese": "{element} có màu sắc đặc trưng nào?",
        "English": "What is the characteristic color of {element}?",
        "category": "Màu sắc"
    },
    "Flame Color": {
        "Vietnamese": "Khi đốt cháy hợp chất của {element}, ngọn lửa có màu gì?",
        "English": "When burning {element} compounds, what color is the flame?",
        "category": "Màu ngọn lửa"
    },
    "Physical State": {
        "Vietnamese": "Ở điều kiện thường, {element} tồn tại ở trạng thái nào?",
        "English": "At room temperature, what is the physical state of {element}?",
        "category": "Trạng thái vật lý"
    },
    "Allotropes": {
        "Vietnamese": "{element} có các dạng thù hình nào?",
        "English": "What are the allotropes of {element}?",
        "category": "Dạng thù hình"
    },

    # --- Priority 3: Chemical Properties & Applications ---
    "Chemical Character": {
        "Vietnamese": "Tính chất hóa học đặc trưng của {element} là gì?",
        "English": "What is the characteristic chemical property of {element}?",
        "category": "Tính chất hóa học"
    },
    "Compound Type": {
        "Vietnamese": "Hợp chất phổ biến của {element} thuộc loại nào?",
        "English": "What type of compound does {element} typically form?",
        "category": "Loại hợp chất"
    },
    "Nature/PH": {
        "Vietnamese": "Môi trường/pH đặc trưng của các hợp chất {element} là gì?",
        "English": "What is the characteristic pH/Nature of {element} compounds?",
        "category": "Môi trường/ pH"
    },
    "Indicator Color Change": {
        "Vietnamese": "Hợp chất của {element} làm đổi màu chất chỉ thị như thế nào?",
        "English": "How do {element} compounds change indicator colors?",
        "category": "Màu chất chỉ thị"
    },
    "Applications": {
        "Vietnamese": "Một trong những ứng dụng phổ biến của {element} là gì?",
        "English": "What is a common application of {element}?",
        "category": "Ứng dụng"
    },
    "Production": {
        "Vietnamese": "Phương pháp chính để điều chế {element} là gì?",
        "English": "What is the main method to produce {element}?",
        "category": "Cách điều chế"
    },
    "Compounds": {
        "Vietnamese": "Đâu là một hợp chất quan trọng của {element}?",
        "English": "Which is an important compound of {element}?",
        "category": "Hợp chất"
    },

    # --- Priority 4: Advanced/Specific ---
    "Reaction Type": {
        "Vietnamese": "Loại phản ứng hóa học đặc trưng của {element} là gì?",
        "English": "What is the characteristic reaction type of {element}?",
        "category": "Loại phản ứng"
    },
    "Minerals/Ores": {
        "Vietnamese": "{element} thường được tìm thấy trong quặng nào?",
        "English": "{element} is typically found in which ore?",
        "category": "Quặng"
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
