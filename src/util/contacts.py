"""Contact utility functions."""

import phonenumbers


def is_phone_number(val: str, region: str) -> bool:
    """Test if a passed string is a phone number."""
    try:
        phonenumbers.parse(val, region)
    except phonenumbers.NumberParseException:
        return False
    else:
        return True


def parse_phone_number(val: str, region: str) -> str:
    """Parse a phone number."""
    number = phonenumbers.parse(val, region)
    return f"+{number.country_code}{number.national_number}"
