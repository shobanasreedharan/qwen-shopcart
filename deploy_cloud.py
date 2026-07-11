import os

print("Alibaba Cloud deployment scaffold")
print("Set the following environment variables before deployment:")
for key in [
    "QWEN_API_KEY",
    "QWEN_BASE_URL",
    "QWEN_MODEL",
    "MONGO_DB",
    "MCP_SERVER_URL",
    "GOOGLE_MAPS_API_KEY",
]:
    print(f"- {key}={os.getenv(key, '')}")
