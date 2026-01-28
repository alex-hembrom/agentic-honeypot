import re

def extract_intel(text):
    """
    Instantly extracts phone numbers, UPIs, and Bank numbers using Regex.
    Also detects the 'nature' of the request.
    """
    text_lower = text.lower()
    
    # 1. Regex Patterns
    patterns = {
        "upi": r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}',
        "bank": r'\b\d{9,18}\b',
        "phone": r'(?:\+91[\-\s]?)?[6-9]\d{9}',
        "link": r'(https?://\S+|www\.\S+)',
        "otp": r'\b\d{4,6}\b' 
    }
    
    # 2. Extract Data
    intel = {
        "bankAccounts": list(set(re.findall(patterns["bank"], text))),
        "upiIds": re.findall(patterns["upi"], text),
        "phoneNumbers": re.findall(patterns["phone"], text),
        "phishingLinks": re.findall(patterns["link"], text),
        "suspiciousKeywords": []
    }

    # 3. Context Keywords (Does the scammer want something?)
    scam_triggers = ["urgent", "verify", "block", "police", "suspended", "kyc", "expire", "winner", "prize"]
    intel["suspiciousKeywords"] = [w for w in scam_triggers if w in text_lower]

    # 4. Final Verdict
    # It is a scam if they ask for money, links, or threaten us.
    has_evidence = any([
        intel["bankAccounts"], 
        intel["upiIds"], 
        intel["phishingLinks"],
        len(intel["suspiciousKeywords"]) > 0
    ])
    
    intel["scamDetected"] = has_evidence
    return intel