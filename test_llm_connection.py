import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Initialize ChatOpenAI configured for BigModel
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

print(f"Connecting to model {llm.model}...")

try:
    response = llm.invoke("Hi! Tell me your name and if you can hear me.")
    print("\n--- Connection Success ---")
    print("Response:")
    print(response.content)
except Exception as e:
    print("\n--- Connection Failed ---")
    print("Error:", e)
