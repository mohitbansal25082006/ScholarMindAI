import os, sys, chromadb, sentence_transformers, streamlit
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

print("✅ All packages imported successfully!")
print("✅ GEMINI_API_KEY loaded:", bool(key))

# Optional ping Gemini
genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Say hello in 3 words.")
print("✅ Gemini reply:", response.text)