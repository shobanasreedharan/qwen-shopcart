import os
from collections import defaultdict


_LIMITS = {
    "generate": int(os.getenv("RATE_LIMIT_GENERATE", "100")),
    "gemini": int(os.getenv("RATE_LIMIT_GEMINI", "50")),
    "chat": int(os.getenv("RATE_LIMIT_CHAT", "100")),
}

_usage = defaultdict(lambda: {"generate": 0, "gemini": 0, "chat": 0})


def _get_state(user_id: str) -> dict:
    return _usage[user_id]


def check_generate_limit(user_id: str) -> dict:
    state = _get_state(user_id)
    used = state["generate"]
    limit = _LIMITS["generate"]
    return {"allowed": used < limit, "used": used, "limit": limit, "message": "Generate limit reached" if used >= limit else ""}


def check_gemini_limit(user_id: str) -> dict:
    state = _get_state(user_id)
    used = state["gemini"]
    limit = _LIMITS["gemini"]
    return {"allowed": used < limit, "used": used, "limit": limit, "message": "Gemini limit reached" if used >= limit else ""}


def check_chat_limit(user_id: str) -> dict:
    state = _get_state(user_id)
    used = state["chat"]
    limit = _LIMITS["chat"]
    return {"allowed": used < limit, "used": used, "limit": limit, "message": "Chat limit reached" if used >= limit else ""}


def increment_usage(user_id: str, kind: str) -> dict:
    state = _get_state(user_id)
    state[kind] = state.get(kind, 0) + 1
    return state
