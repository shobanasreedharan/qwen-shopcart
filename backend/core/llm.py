import json
import os
from dotenv import load_dotenv

from backend.core.qwen_client import generate_text

load_dotenv()


class GeminiPlanner:

    def decide_next_action(self, state):

        prompt = f"""
You are a grocery AI agent.

Current state:
{json.dumps(state, indent=2)}

Choose ONE action:
- GET_INGREDIENTS
- CHECK_PANTRY
- OPTIMIZE_BUDGET
- FIND_STORES
- ROUTE
- FINALIZE

Return JSON:
{{
  "type": "ACTION_NAME"
}}
"""

        response = generate_text(prompt)

        try:
            return json.loads(response)
        except Exception:
            return {"type": "FINALIZE"}