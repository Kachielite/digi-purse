from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health Check"])


# Health Check
@router.get("/")
def check_health():
    return {"status": "System Healthy"}

