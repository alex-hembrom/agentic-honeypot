import os
from dotenv import load_dotenv
import google.generativeai as genai

print("--- DIAGNOSTIC MODE ---")

# 1. Try to load the .env file
is_loaded = load_dotenv()
print(f"1. .env file found? {is_loaded}")

# 2. Check the Variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: Python cannot find 'GEMINI_API_KEY'.")
else:
    print(f"2. Key loaded successfully: {api_key[:5]}*******")

# 3. Test the Connection to Google
print("3. Attempting to contact Google AI...")
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Are you online?")
    
    print("\n✅ SUCCESS! The AI replied:")
    print(f"\"{response.text.strip()}\"")
    print("\nCONCLUSION: Your keys are fine. The issue was likely just a restart needed.")

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    print("Read the error above. It tells you exactly what is wrong (e.g., Quota Exceeded, Invalid Key).")