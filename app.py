import os
import json
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv  # <--- NEW IMPORT

# Load the secret .env file
load_dotenv()

app = Flask(__name__)

# --- 1. CONFIGURATION ---
# Now we fetch the keys from the secure environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HACKATHON_API_KEY = os.getenv("HACKATHON_API_KEY")

# Debugging: Check if keys are loaded correctly
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env file!")
else:
    print("✅ GEMINI_API_KEY loaded successfully.")

if not HACKATHON_API_KEY:
    print("❌ Error: HACKATHON_API_KEY not found in .env file!")
else:
    print("✅ HACKATHON_API_KEY loaded successfully.")


# Configure the AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. AI FUNCTIONS ---

def analyze_with_ai(message, history):
    """
    Asks AI to detect scam, generate a reply, and extract data in ONE step.
    This is faster than making 3 separate calls.
    """
    if not GEMINI_API_KEY:
        return {
            "scamDetected": False,
            "reply": "System Error: AI Key missing.",
            "intelligence": {},
            "reason": "Configuration Error"
        }

    prompt = f"""
    You are an AI Scam Baiting Agent. You are acting as a naive, slightly confused elderly person named "Grandpa Joe".
    
    INCOMING MESSAGE: "{message}"
    CHAT HISTORY: {history}
    
    TASK:
    1. Analyze if this is a scam.
    2. Generate a reply. If it is a scam, reply as Grandpa Joe to waste their time. If not, reply normally.
    3. Extract any phone numbers, UPI IDs, banks, or links.
    
    OUTPUT JSON FORMAT ONLY:
    {{
        "scamDetected": true/false,
        "reply": "Your reply text here",
        "intelligence": {{
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }},
        "reason": "Why you think it is a scam"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        # Fallback if AI fails
        return {
            "scamDetected": True,
            "reply": "I am having trouble reading this. Can you call me?",
            "intelligence": {"bankAccounts": [], "upiIds": [], "phishingLinks": []},
            "reason": "AI Error"
        }

def send_callback_to_guvi(session_id, scam_detected, total_messages, intelligence, notes):
    """
    Sends the MANDATORY final report to the Hackathon System.
    """
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": notes
    }
    
    try:
        # We use a short timeout because we don't want to hang our server
        requests.post(url, json=payload, timeout=2)
        print(f"[-] Callback sent for Session {session_id}")
    except Exception as e:
        print(f"[!] Callback Failed (This is normal during testing): {e}")

# --- 3. THE SERVER ---

@app.route('/webhook', methods=['POST'])
def handle_message():
    try:
        # Security Check
        incoming_key = request.headers.get('x-api-key')
        if incoming_key != HACKATHON_API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Get Data
        data = request.json
        session_id = data.get("sessionId", "unknown")
        incoming_msg = data.get("message", {}).get("text", "")
        history = data.get("conversationHistory", [])
        
        print(f"\n[+] Processing Message from {session_id}...")

        # CALL THE AI
        ai_result = analyze_with_ai(incoming_msg, history)
        
        # Prepare the mandatory Callback (Fire and forget)
        if ai_result["scamDetected"]:
            send_callback_to_guvi(
                session_id, 
                True, 
                len(history) + 1, 
                ai_result["intelligence"], 
                ai_result["reason"]
            )

        # Construct the Response for the Immediate Request
        response_payload = {
            "status": "success",
            "scamDetected": ai_result["scamDetected"],
            "engagementMetrics": {
                "engagementDurationSeconds": 5,
                "totalMessagesExchanged": len(history) + 1
            },
            "extractedIntelligence": ai_result["intelligence"],
            "agentNotes": ai_result["reply"] # We send our reply in the notes/reply field
        }
        
        return jsonify(response_payload), 200

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return "AI Honey-Pot is Brainy and Online!", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)