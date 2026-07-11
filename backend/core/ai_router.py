from backend.core.qwen_client import generate_text
from backend.ai.fallback_engine import fallback_ingredients


def safe_ai_generate(prompt: str):
    try:
        result = generate_text(prompt)

        if result is None or result == "":
            raise ValueError("Empty Qwen response")

        return result

    except Exception as e:
        print("[AI Router] Qwen failed → fallback used:", e)
        return "Fallback response: " + str(fallback_ingredients({"fallback": prompt}))