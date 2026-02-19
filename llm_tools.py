# llm_tools.py

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ===== LANGSMITH CONFIG =====
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Autonomous-Learning-Agent")

# 🔥 IMPORTANT: disable background thread (Windows fix)
os.environ["LANGCHAIN_CALLBACKS_BACKGROUND"] = "false"

print("✅ LANGSMITH:", os.getenv("LANGCHAIN_TRACING_V2"))
print("✅ PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("✅ KEY FOUND:", bool(os.getenv("LANGCHAIN_API_KEY")))

from langchain_groq import ChatGroq


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    api_key=os.getenv("your_api_key"),
)

search_tool = TavilySearch(k=3, api_key=os.getenv("your_api_key"))


