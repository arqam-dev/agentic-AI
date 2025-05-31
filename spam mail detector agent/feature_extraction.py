import re
def extract_features(text):
    return {
        'has_urgent': int(bool(re.search(r'\b(urgent|immediate|act now|limited time)\b', text, re.I))),
        'has_winner': int(bool(re.search(r'\b(win|winner|won|prize|reward|free|gift)\b', text, re.I))),
        'has_link': int(bool(re.search(r'http[s]?://|www\.', text))),
        'has_number': int(bool(re.search(r'\d{10,}', text))),
        'has_special_chars': int(bool(re.search(r'[!$%^&*()_+|~={}\[\]:";\'<>?,./]', text))),
        'has_caps': int(sum(1 for c in text if c.isupper()) / len(text) > 0.3 if text else 0),
        'length': len(text)
    }
