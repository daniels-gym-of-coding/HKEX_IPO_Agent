import os
import sys
import json
from dotenv import load_dotenv


from modules.read_research_topic import read_research_topic

from modules.analyze_user_prompt import analyze_user_prompt

# Load environment variables from .env
load_dotenv()

# Read the research topic prompt
file_path = "research_topic.txt"
prompt = read_research_topic(file_path)

print(f"Analyzing prompt from {file_path}...")

parsed = analyze_user_prompt(prompt)

if parsed:
    print("\n--- Success ---")
    print("Parsed Parameters:")
    print(json.dumps(parsed, indent=2))
else:
    print("\n--- Failed ---")
    print("Failed to analyze user prompt.")


