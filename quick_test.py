from backend.core.qwen_client import generate_text
 
result = generate_text('Return JSON only, no markdown: {"type": "TEST"}')
print("Raw response:")
print(result)