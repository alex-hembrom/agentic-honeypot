import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_reply(history, intel):
    """
    Decides what to say based on what we found (Intel).
    """
    # Dynamic Persona Injection
    persona = "You are Grandpa Joe, 78. You are confused and type slowly."
    
    strategy = "Act confused."
    if intel['bankAccounts']:
        strategy = "They sent a bank account! Pretend you are trying to send money but getting an error. Ask for the IFSC code to waste time."
    elif intel['upiIds']:
        strategy = "They sent a UPI! Say you don't have GPay. Ask if you can deposit cash at the bank."
    
    prompt = f"""
    {persona}
    STRATEGY: {strategy}
    
    HISTORY: {history}
    
    Write a short (1-2 sentence) reply. Make 1 spelling mistake to look real.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "wait... my glasses fell. what did u say?"