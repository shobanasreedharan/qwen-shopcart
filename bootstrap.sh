#!/bin/bash
set -e

# FC custom runtime — installs dependencies on cold start, then launches uvicorn
# on the port FC expects (set via s.yaml customRuntimeConfig.port -> $FC_SERVER_PORT)

python3 -m pip install --no-cache-dir -r requirements.txt

python3 -m uvicorn backend.api.main:app \
    --host 0.0.0.0 \
    --port ${FC_SERVER_PORT:-9000}
    
