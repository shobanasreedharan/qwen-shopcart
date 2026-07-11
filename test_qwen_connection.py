"""
test_qwen_connection.py

Standalone sanity check for your Qwen Cloud (Model Studio) API key and endpoint —
run this BEFORE touching llm.py / ai_router.py, so we know the credentials
and region/base URL are correct in isolation.

Usage:
    pip install openai --break-system-packages   (if not already installed)
    set QWEN_API_KEY=sk-xxxxx                     (Windows CMD)
    $env:QWEN_API_KEY="sk-xxxxx"                   (PowerShell)
    python test_qwen_connection.py
"""

import os
import sys
import time

from openai import OpenAI

# ---- CONFIG ------------------------------------------------------------
# Pick the base URL matching the REGION your API key was created in.
# These are NOT interchangeable — a Singapore key will not work against
# the China base URL, and vice versa.

BASE_URLS = {
    "singapore": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "us_virginia": "https://dashscope-us.aliyuncs.com/compatible-mode/v1",  # intl endpoint also serves US region
    "china_beijing": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

# Change this to match the region you created your API key in
REGION = "singapore"

MODEL = "qwen-plus"  # good default: balances cost/speed/quality

# ---- SCRIPT --------------------------------------------------------------

def main():
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("ERROR: QWEN_API_KEY (or DASHSCOPE_API_KEY) environment variable not set.")
        print("Set it first, e.g.:")
        print('  $env:QWEN_API_KEY="sk-xxxxx"   (PowerShell)')
        sys.exit(1)

    if REGION not in BASE_URLS:
        print(f"ERROR: Unknown region '{REGION}'. Choose from: {list(BASE_URLS.keys())}")
        sys.exit(1)

    base_url = BASE_URLS[REGION]

    print(f"Region:    {REGION}")
    print(f"Base URL:  {base_url}")
    print(f"Model:     {MODEL}")
    print(f"API key:   {api_key[:6]}...{api_key[-4:]}  (masked)")
    print("-" * 60)

    client = OpenAI(api_key=api_key, base_url=base_url)

    test_prompt = "Reply with exactly one short sentence confirming you are Qwen and working."

    try:
        start = time.time()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": test_prompt},
            ],
        )
        elapsed = time.time() - start

        content = response.choices[0].message.content
        usage = response.usage

        print("SUCCESS")
        print(f"Response ({elapsed:.2f}s): {content}")
        print("-" * 60)
        print(f"Prompt tokens:     {usage.prompt_tokens}")
        print(f"Completion tokens: {usage.completion_tokens}")
        print(f"Total tokens:      {usage.total_tokens}")

    except Exception as e:
        print("FAILED")
        print(f"Error: {e}")
        print("-" * 60)
        print("Common causes:")
        print("  - Wrong region/base URL for this API key (keys are region-locked)")
        print("  - API key not activated / Model Studio not activated in this region")
        print("  - Using a Coding Plan key (sk-sp-xxx) instead of a regular key (sk-xxx)")
        print("  - Coupon/quota exhausted or not yet applied")
        sys.exit(1)


if __name__ == "__main__":
    main()
