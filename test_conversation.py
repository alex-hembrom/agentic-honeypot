import requests
import json
import time

URL = "http://127.0.0.1:5000/webhook"
API_KEY = "my-secret-password-123"

# Message 1: The Hook
msg1 = {
  "sessionId": "demo-chat-001",
  "message": {"sender": "scammer", "text": "URGENT: Your Account is blocked. Verify now!"},
  "conversationHistory": []
}

# Message 2: The Demand (Simulating a reply after you said something)
msg2 = {
  "sessionId": "demo-chat-001",
  "message": {"sender": "scammer", "text": "Click this link http://steal.com/login to unlock."},
  "conversationHistory": [
      {"sender": "scammer", "text": "URGENT: Your Account is blocked."},
      {"sender": "user", "text": "what? who is this? i dont understand"}
  ]
}

def send_msg(step, payload):
    print(f"\n📨 Sending Message {step}...")
    headers = {"x-api-key": API_KEY}
    try:
        res = requests.post(URL, json=payload, headers=headers)
        data = res.json()
        print(f"🤖 Bot Reply: \"{data['agentNotes']}\"")
        print(f"🕵️ Internal Notes: {data.get('extractedIntelligence', {}).get('scamDetected')}")
    except Exception as e:
        print(f"Error: {e}")

# Run the conversation
send_msg(1, msg1)
time.sleep(1)
send_msg(2, msg2)