from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health check"])


# Health Check
@router.get("/")
def check_health():
    return {"status": "System Healthy"}

