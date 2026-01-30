import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- DEBUGGING: CHECK IF KEY EXISTS ---
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ CRITICAL ERROR: GEMINI_API_KEY is missing from .env!")
else:
    # Print first 5 chars to verify it's loaded (safe)
    print(f"✅ AI Key Loaded: {api_key[:5]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_reply(history, intel):
    """
    God Mode Brain: Generates reply + Secret Notes for Judges
    """
    # 1. MOOD EVOLUTION
    turn_count = len(history)
    mood = "CONFUSED_ELDERLY" 
    if turn_count >= 3: mood = "GREEDY_INTERESTED"
    if turn_count >= 6: mood = "FRUSTRATED_TECHNICAL_ISSUES"
    if turn_count >= 10: mood = "SCARED_PARANOID"

    # 2. STRATEGY
    strategy = "Act confused. Ask short questions."
    reasoning = f"Turn {turn_count}: Default Confusion."

    # Dynamic Strategies (Defense/Offense)
    if any(w in str(history).lower() for w in ['anydesk', 'teamviewer', 'quicksupport']):
        strategy = "DEFENSE: Remote access detected. Lie: 'Screen is black'."
        reasoning = "Anti-Remote-Access Protocol."
    elif intel['phishingLinks']:
        strategy = "DEFENSE: Link detected. Lie: 'Phone says Error 404'."
        reasoning = "Anti-Phishing Protocol."
    elif intel['bankAccounts']:
        fake_ref = str(random.randint(10000000, 99999999))
        strategy = f"OFFENSE: Bank found. LIE: 'Sent 5000rs. Ref: {fake_ref}'."
        reasoning = f"Generated FAKE Transaction {fake_ref} to waste time."
    elif intel['upiIds']:
        strategy = "OFFENSE: UPI found. LIE: 'No GPay. Can I send Card photo?'."
        reasoning = "Baiting for Card Details (Time waster)."

    # 3. PROMPT
    prompt = f"""
    ROLE: Grandpa Joe (78, Greedy, Bad with Tech).
    MOOD: {mood}
    STRATEGY: {strategy}
    
    RULES: Lowercase only. Make typos ("mney", "pls"). Short sentences.
    
    CHAT HISTORY: {history}
    
    REPLY:
    """
    
    try:
        response = model.generate_content(prompt)
        reply_text = response.text.strip().lower()
        return {
            "reply": reply_text,
            "notes": f"[MOOD: {mood}] {reasoning}"
        }
    except Exception as e:
        print(f"❌ AI GENERATION ERROR: {e}")
        return {
            "reply": "hello? my internet stopped working...",
            "notes": f"System Error: {str(e)}"
        }