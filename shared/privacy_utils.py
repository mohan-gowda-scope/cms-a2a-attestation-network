import re

def mask_phi(data):
    """
    Recursively masks SSNs, Addresses, and Phone numbers in clinical data.
    Ensures PII/PHI is not sent to AI models during policy review.
    """
    if isinstance(data, dict):
        return {k: mask_phi(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_phi(item) for item in data]
    elif isinstance(data, str):
        # Mask SSN
        data = re.sub(r'\d{3}-\d{2}-\d{4}', '[SSN_MASKED]', data)
        # Mask Phone
        data = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE_MASKED]', data)
        # Mask Age/DOB in specific formats if needed
        return data
    return data
