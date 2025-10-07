import phonenumbers

def validate_e164(phone):
    """Validate E.164 phone number format"""
    try:
        p = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(p)
    except Exception:
        return False

def normalize_phone(phone):
    """Normalize phone number to E.164 format"""
    try:
        p = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return phone