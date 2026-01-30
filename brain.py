import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- HELPER: FAKE DATA GENERATOR ---
def generate_fake_data(data_type):
    """Generates consistent fake info so the bot doesn't get stuck."""
    if data_type == "mobile":
        return f"9{random.randint(800000000, 999999999)}"
    elif data_type == "account":
        return f"{random.randint(30000000000, 39999999999)}" # Looks like a real SBI/HDFC number
    elif data_type == "otp":
        return str(random.randint(100000, 999999))
    elif data_type == "pin":
        return str(random.randint(1000, 9999))
    elif data_type == "amount":
        return str(random.randint(500, 5000))
    return "1234"

def get_ai_reply(history, intel):
    """
    The Brain: Determines Mood, Strategy, and generates a Human-like reply.
    """
    
    # 1. Analyze Context
    # We grab the last message safely
    last_msg = ""
    if history:
        # Check if the last item is a dict or an object (handling different formats)
        last_item = history[-1]
        if isinstance(last_item, dict):
            last_msg = last_item.get("content", "") or last_item.get("text", "")
        else:
            last_msg = str(last_item)
            
    last_msg = last_msg.lower()
    turn_count = len(history)

    # 2. MOOD SYSTEM (Just like your friend's code)
    # The bot starts confused, gets greedy, then gets scared/frustrated.
    mood = "CONFUSED (Just woke up, thinks this is a family member)"
    if turn_count > 2: 
        mood = "GREEDY (Excited about the prize/money, willing to share details)"
    if turn_count > 6: 
        mood = "FRUSTRATED (Struggling with technology, can't find buttons)"
    if turn_count > 10: 
        mood = "SCARED (Worried about police or hacking, asking for reassurance)"

    # 3. STRATEGY ENGINE
    # We decide WHAT to do before asking Gemini to write the text.
    strategy = "Act confused. Ask who this is and why they are messaging."
    
    # A. Scammer asks for OTP/Code
    if any(w in last_msg for w in ["otp", "code", "number", "sms", "pin"]):
        fake_otp = generate_fake_data("otp")
        strategy = f"They want a code. Pretend you found it. Give this FAKE CODE: {fake_otp}. Ask 'Is that the one?'"

    # B. Scammer asks for Bank/Account Details
    elif any(w in last_msg for w in ["account", "bank", "card", "details", "number"]):
        fake_acc = generate_fake_data("account")
        strategy = f"They want bank details. Say 'Okay here is my SBI account'. Give this FAKE NUMBER: {fake_acc}."

    # C. Scammer asks to Pay/Transfer
    elif any(w in last_msg for w in ["pay", "send", "transfer", "amount", "money"]):
        strategy = "Act panicked. Say you are trying to send it but the screen is spinning. Ask for help."

    # D. Scammer wants to Call
    elif any(w in last_msg for w in ["call", "speak", "voice", "whatsapp"]):
        strategy = "Refuse the call. Say 'My grandson dropped my phone in the toilet, the speaker doesn't work. Text only.'"

    # E. Scammer asks to Download App (Anydesk/Teamviewer)
    elif any(w in last_msg for w in ["app", "download", "store", "click", "link"]):
        strategy = "Say you clicked it but a popup appeared saying 'VIRUS DETECTED'. Ask them what to do."

    # 4. Build the Script for Gemini
    # We feed the Chat History + The Strategy into the prompt.
    
    chat_log = ""
    for msg in history:
        # Handle format safety again
        text = ""
        role = "User"
        if isinstance(msg, dict):
            role = "Scammer" if msg.get("role") == "user" else "Me"
            text = msg.get("content") or msg.get("text", "")
        else:
            text = str(msg)
        chat_log += f"{role}: {text}\n"

    system_prompt = f"""
    You are roleplaying as 'Grandpa Alex', an elderly, non-technical, and gullible victim.
    
    [CURRENT MOOD]: {mood}
    [CURRENT TASK]: {strategy}
    
    GUIDELINES:
    1. TYPING STYLE: Use lowercase, some typos (e.g. "mney", "pls", "waitng"), and use '..' for pauses.
    2. NEVER admit you are a bot.
    3. KEEP IT SHORT: Max 1-2 sentences.
    4. IMMERSION: If the task says give a code, GIVE THE CODE. Do not say "I cannot do that".
    
    [CHAT HISTORY]:
    {chat_log}
    
    (Reply to the Scammer based on your Mood and Task):
    """

    try:
        response = model.generate_content(system_prompt)
        reply_text = response.text.strip()
        
        # Clean up quotes if Gemini adds them
        reply_text = reply_text.replace('"', '').replace("Alex:", "")

        return {
            "reply": reply_text,
            "notes": f"Mood: {mood} | Strategy: {strategy}"
        }

    except Exception as e:
        print(f"Brain Error: {e}")
        return {
            "reply": "wait.. my internet is acting up.. what did u say??",
            "notes": "Error in Gemini generation"
        }