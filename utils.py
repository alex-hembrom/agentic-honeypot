import re

def extract_intel(text):
    """
    Instantly extracts phone numbers, UPIs, and Bank numbers using Math (Regex).
    This is 100x faster than asking AI to do it.
    """
    intel = {
        "bankAccounts": list(set(re.findall(r'\b\d{9,18}\b', text))),
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "phoneNumbers": re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}', text),
        "phishingLinks": re.findall(r'(https?://\S+|www\.\S+)', text),
        "suspiciousKeywords": [w for w in ["urgent", "verify", "block", "police"] if w in text.lower()]
    }
    # If we found any of these, it is likely a scam
    intel["scamDetected"] = any(intel.values())
    return intel