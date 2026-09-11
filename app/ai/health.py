from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("", response_model=dict)
def health():
    return {
        "status": "ok"
    }