
def clean_phone_number(phone_number):
    """Clean phone number or LID by removing @c.us or @lid suffixes."""
    if not phone_number:
        return phone_number
    phone_number = str(phone_number)
    if "@c.us" in phone_number: 
        phone_number = phone_number.split("@")[0]
        return phone_number
    if "@lid" in phone_number:
        phone_number = phone_number.split("@")[0]
        return phone_number
    return phone_number
