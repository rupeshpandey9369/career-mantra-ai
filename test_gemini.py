import google.generativeai as genai

# ====== APNA API KEY DALO ======
genai.configure(api_key="AIAIzaSyDAKor1ZNkcJ1ADhne__5eyvd435kTZVYQ")  # YE EDIT KARO!

print("🔄 Testing...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello!")
    print("✅ GEMINI WORKING!")
    print("🤖", response.text[:200])
except Exception as e:
    print("❌", str(e))
