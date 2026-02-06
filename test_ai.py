import google.generativeai as genai

# আপনার API Key
GEMINI_API_KEY = "AIzaSyByv_7z9rCMmtVc4reEueUb69n9u5k5iuQ"

genai.configure(api_key=GEMINI_API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")