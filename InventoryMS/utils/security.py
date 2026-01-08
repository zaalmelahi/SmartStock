import re

def sanitize_input(value, allowed_chars=None):
    """
    Sanitizes a string input by removing potentially dangerous characters.
    
    Args:
        value: The input string to sanitize.
        allowed_chars: A regex pattern of allowed characters. If None, 
                       it allows alphanumeric and common safe punctuation.
    """
    if not isinstance(value, str):
        return value
    
    if allowed_chars is None:
        # Default: Allow alphanumeric, spaces, and basic punctuation (_, -, ., @)
        allowed_chars = r"[^a-zA-Z0-9\s\_\-\.\@]"
    
    # Remove characters NOT in the allow list
    sanitized = re.sub(allowed_chars, '', value)
    
    # Also strip known SQL comment characters as an extra layer of defense
    sanitized = sanitized.replace('--', '').replace('/*', '').replace('*/', '').replace(';', '')
    
    return sanitized.strip()

def escape_sql_special_chars(value):
    """
    Escapes special characters that could be used in SQL queries.
    Note: Always prefer Django ORM or parameterized queries over this.
    """
    if not isinstance(value, str):
        return value
        
    # Manual escaping (as a last resort defense)
    replacements = {
        "'": "''",
        "\\": "\\\\",
        "\0": "\\0",
        "\n": "\\n",
        "\r": "\\r",
        "\032": "\\Z",
    }
    
    for char, replacement in replacements.items():
        value = value.replace(char, replacement)
        
    return value
