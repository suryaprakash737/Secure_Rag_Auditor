from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from app.config import API_KEYS

api_key_header = APIKeyHeader(name="X-API-Key")

def get_clearance(api_key: str = Security(api_key_header)) -> int:
    clearance = API_KEYS.get(api_key)
    if clearance is None:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return clearance