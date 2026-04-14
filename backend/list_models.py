import os
import google.generativeai as genai
import sys

api_key = sys.argv[1]
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"Name: {m.name}")
        print(f"Display Name: {m.display_name}")
        print(f"Description: {m.description}")
        print("-" * 40)
