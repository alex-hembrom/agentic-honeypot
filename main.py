from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
import uvicorn
import requests
import os
from dotenv import load_dotenv
from brain import get_ai_reply
from utils import extract_intel

# Load Keys
load_dotenv()
HACKATHON_API_KEY = os.getenv("HACKATHON_API_KEY")

app = FastAPI()

# --- 1. NEW: HOME PAGE (Fixes the 404 Error) ---
@app.get("/")
def home():
    return {"message": "Alex's AI Agent is awake and running!"}

# --- BACKGROUND TASK ---
def send_callback(session_id, scam_detected, total_msgs, intel, notes):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_msgs,
        "extractedIntelligence": intel,
        "agentNotes": notes  # <--- Now sending detailed reasoning
    }
    try:
        requests.post(url, json=payload, timeout=2)
        print(f"[-] Callback sent for {session_id}")
    except:
        pass

@app.post("/webhook")
async def handle_chat(request: Request, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # 1. Security
    if x_api_key != HACKATHON_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Parse
    data = await request.json()
    session_id = data.get("sessionId", "unknown")
    user_text = data.get("message", {}).get("text", "")
    history = data.get("conversationHistory", [])

    print(f"\n[+] Msg from {session_id}: {user_text}")

    # 3. Analyze (Regex)
    intel = extract_intel(user_text)
    
    # 4. Think (Brain)
    # bot_result is now a DICTIONARY: {"reply": "...", "notes": "..."}
    bot_result = get_ai_reply(history, intel)
    
    bot_reply = bot_result["reply"]
    agent_notes = bot_result["notes"]

    # 5. Report (Background)
    if intel["scamDetected"]:
        background_tasks.add_task(
            send_callback, 
            session_id, 
            True, 
            len(history) + 1, 
            intel, 
            agent_notes # Sending the clever reasoning
        )

    # 6. Respond
    return {
        "status": "success",
        "scamDetected": intel["scamDetected"],
        "engagementMetrics": {
            "engagementDurationSeconds": 5,
            "totalMessagesExchanged": len(history) + 1
        },
        "extractedIntelligence": intel,
        "agentNotes": bot_reply # To the scammer, we just send the text
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)