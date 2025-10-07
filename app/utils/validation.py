from app.utils.phone_utils import validate_e164, normalize_phone

def validate_phone(phone):
    """Validate phone number"""
    normalized = normalize_phone(phone)
    return validate_e164(normalized), normalized

def validate_template(template_body, placeholders):
    """Validate template syntax and placeholders"""
    try:
        from app.utils.template_utils import render_template_text
        render_template_text(template_body, placeholders)
        return True, None
    except Exception as e:
        return False, str(e)