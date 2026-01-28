import requests
import json

# --- CONFIGURATION ---
# We test your LOCAL running server directly
URL = "http://127.0.0.1:5000/webhook" 
API_KEY = "my-secret-password-123"

# --- THE TEST MESSAGE ---
payload = {
  "sessionId": "test-session-001",
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your SBI account is blocked. Click http://bit.ly/steal or send money to scammer@upi to verify."
  },
  "conversationHistory": []
}

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

print(f"📡 Sending Test to: {URL}...")

try:
    response = requests.post(URL, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Here is the JSON your bot sent back:")
        print("-" * 40)
        print(json.dumps(response.json(), indent=2))
        print("-" * 40)
    else:
        print(f"❌ ERROR: {response.text}")

except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("Make sure 'python main.py' is running in another terminal!")