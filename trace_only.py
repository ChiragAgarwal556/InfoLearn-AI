from llm_tools import llm
from langsmith import Client

print("Calling LLM...")
resp = llm.invoke("TRACE TEST AFTER FIX")
print(resp.content)

# ✅ Correct way to flush traces
client = Client()
client.flush()

print("Trace flushed successfully")
