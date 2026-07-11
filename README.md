# SmartCart AI

SmartCart AI is a grocery planning assistant that now uses a Qwen-compatible model for recipe generation, meal planning, chat responses, and related AI flows.

## Features
- Meal planning and shopping list generation
- Pantry-aware suggestions
- Recipe caching and substitution handling
- Qwen-compatible API integration

## Environment
Create a `.env` file based on `.env.example` and set:
- `QWEN_API_KEY`
- `QWEN_BASE_URL`
- `QWEN_MODEL`
- `MONGO_DB`
- `MCP_SERVER_URL`

## Run locally
```bash
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

## Deploy
Use the provided Dockerfile or deployment scripts after setting your cloud environment variables.
