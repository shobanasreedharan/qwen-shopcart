import os
import json
import firebase_admin
from firebase_admin import credentials

# Service account key downloaded from:
# Firebase Console > Project Settings > Service Accounts > Generate new private key
#
# Credential resolution order:
#   1. FIREBASE_CREDENTIALS_JSON env var (JSON content as a string) — used on
#      Alibaba Cloud Function Compute, where we don't ship the key file itself
#   2. serviceAccountKey.json file — used for local dev
#   3. Application default / project-id-only fallback

firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if firebase_creds_json:
    cred_dict = json.loads(firebase_creds_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
elif os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
else:
    firebase_admin.initialize_app(options={"projectId": os.getenv("GOOGLE_CLOUD_PROJECT", "smartcart")})
    