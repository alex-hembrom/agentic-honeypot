from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
import uvicorn
import requests
import os
from dotenv import load_dotenv
from brain import get_ai_reply
from utils import extract_intel

load_dotenv()

app = FastAPI()
HACKATHON_API_KEY = os.getenv("HACKATHON_API_KEY")

# Background Task to send data to GUVI without slowing down the bot
def send_callback(session_id, scam_detected, total_msgs, intel, notes):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_msgs,
        "extractedIntelligence": intel,
        "agentNotes": notes
    }
    try:
        requests.post(url, json=payload, timeout=5)
        print(f"[-] Callback sent for {session_id}")
    except:
        pass

@app.post("/webhook")
async def handle_chat(request: Request, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # 1. Security
    if x_api_key != HACKATHON_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Parse Data
    data = await request.json()
    session_id = data.get("sessionId", "unknown")
    user_text = data.get("message", {}).get("text", "")
    history = data.get("conversationHistory", [])

    # 3. FAST Analysis (Regex first, then AI)
    intel = extract_intel(user_text)
    
    # 4. Smart Brain Reply
    bot_reply = get_ai_reply(history, intel)

    # 5. Fire-and-Forget Callback (This makes your bot faster than your teammate's)
    if intel["scamDetected"]:
        background_tasks.add_task(
            send_callback, 
            session_id, 
            True, 
            len(history)+1, 
            intel, 
            f"Bot replied: {bot_reply}"
        )

    # 6. Response
    return {
        "status": "success",
        "scamDetected": intel["scamDetected"],
        "engagementMetrics": {
            "engagementDurationSeconds": 5,
            "totalMessagesExchanged": len(history) + 1
        },
        "extractedIntelligence": intel,
        "agentNotes": bot_reply
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)