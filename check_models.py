import os
from dotenv import load_dotenv
from google import genai


# 1. Load the environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found. Check your .env file.")
    exit()

# 2. Configure the client
try:
    client = genai.Client(api_key=api_key)
    
    print(f"✅ Authenticated successfully with key: ...{api_key[-4:]}")
    print("\n🔍 Fetching available models that support text generation...\n")

    # 3. List models
    count = 0
    for m in client.models.list():
        # We only care about models that can generate content (chat/text)
        if 'generateContent' in m.supported_actions:
            print(f" • {m.name}")
            print(f"   (Display Name: {m.display_name})")
            print("-" * 40)
            count += 1

    if count == 0:
        print("⚠️ No content generation models found. Your API key might lack permissions.")
    else:
        print(f"\n✨ Found {count} usable models.")

except Exception as e:
    print(f"❌ Connection failed: {e}")