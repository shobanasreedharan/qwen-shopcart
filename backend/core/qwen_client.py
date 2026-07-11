"""
backend/core/qwen_client.py

Thin wrapper around Alibaba Cloud Model Studio (Qwen Cloud), replacing the
Gemini/Vertex AI call site. Exposes generate_text(prompt) -> str, matching
what llm.py (GeminiPlanner) already expects.

Env vars required (see .env):
    QWEN_API_KEY   - Model Studio API key (sk-xxx), region-matched to QWEN_BASE_URL
    QWEN_BASE_URL  - defaults to Singapore endpoint if not set
    QWEN_MODEL     - defaults to "qwen-plus" if not set
"""

import os
import logging

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---- Config ---------------------------------------------------------------

QWEN_API_KEY = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_VL_MODEL = os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")

if not QWEN_API_KEY:
    logger.warning(
        "QWEN_API_KEY is not set. Calls to generate_text() will fail until "
        "it is configured in your .env file."
    )

_client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)


# ---- Public interface -------------------------------------------------------

def generate_text(prompt: str, system_prompt: str = "You are a helpful assistant.",
                   temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """
    Send a prompt to Qwen Cloud and return the raw text response.

    Mirrors the previous Gemini/Vertex call signature used in llm.py —
    callers pass a single prompt string and get a string back (often JSON
    text that the caller then json.loads()'s themselves).
    """
    if not QWEN_API_KEY:
        raise RuntimeError("QWEN_API_KEY is not configured. Set it in .env before calling generate_text().")

    try:
        response = _client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Qwen Cloud call failed: {e}")
        raise


def generate_text_with_image(prompt: str, image_base64: str,
                              system_prompt: str = "You are a helpful assistant.",
                              temperature: float = 0.3, max_tokens: int = 1024) -> str:
    """
    Send a prompt + image to a Qwen vision-language model and return the raw
    text response. Used for receipt parsing (image -> structured JSON).

    image_base64 should be the raw base64 string (no data URI prefix) —
    this function adds the 'data:image/jpeg;base64,' prefix itself.
    """
    if not QWEN_API_KEY:
        raise RuntimeError("QWEN_API_KEY is not configured. Set it in .env before calling generate_text_with_image().")

    try:
        response = _client.chat.completions.create(
            model=QWEN_VL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                },
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Qwen Cloud vision call failed: {e}")
        raise