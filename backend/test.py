import google.generativeai as genai

# Your API key 
API_KEY = "AIzaSyCqNI95axOXHF53c4SDtElyZ75F__mMKwY"

# Configure the API
genai.configure(api_key=API_KEY)

# Print all available models (with more details)
print("=== AVAILABLE MODELS ===")
models = genai.list_models()
for model in models:
    print(f"Model: {model.name}")
    print(f"  - Display name: {model.display_name}")
    print(f"  - Description: {model.description}")
    print(f"  - Supported generation methods:")
    for method in model.supported_generation_methods:
        print(f"    * {method}")
    print("---")

# Try each of the Gemini models with generateContent capability
test_models = [
    model.name.split('/')[-1] for model in models 
    if "gemini" in model.name and "generateContent" in model.supported_generation_methods
]

print("\n=== TESTING MODELS ===")
for model_name in test_models:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, please respond with just 'Test successful'")
        print(f"Response: {response.text}")
        print("✓ Success!")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

print("\nTest complete. If any model succeeded, use that one in your main script.")