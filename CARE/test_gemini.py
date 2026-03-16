import google.generativeai as genai

genai.configure(api_key="AIzaSyDAKor1ZNkcJ1ADhne__5eyvd435kTZVYQ")  # APNA KEY

print("🔍 FINDING AVAILABLE MODELS...")
try:
    # List ALL available models
    models = genai.list_models()
    print("✅ AVAILABLE MODELS:")
    for m in models:
        print(f"  • {m.name}")
        if 'generateContent' in m.supported_generation_methods:
            print(f"     ✅ SUPPORTS CHAT!")
    
    # Try first chat-capable model
    for model_info in models:
        if 'generateContent' in model_info.supported_generation_methods:
            model_name = model_info.name.split('/')[-1]
            print(f"\n🤖 TESTING: {model_name}")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello!")
                print("✅ SUCCESS WITH:", model_name)
                print("🤖", response.text[:200])
                break
            except:
                continue
except Exception as e:
    print("❌", str(e))
