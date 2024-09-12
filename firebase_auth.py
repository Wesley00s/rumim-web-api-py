from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException

FIREBASE_PROJECT_ID = "teste_ruminweb"

def verify_firebase_token(id_token_str: str):
    try:
        decoded_token = id_token.verify_oauth2_token(id_token_str, requests.Request(), FIREBASE_PROJECT_ID)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
