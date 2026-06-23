from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {"status": "The Secure Vault is Online"}
