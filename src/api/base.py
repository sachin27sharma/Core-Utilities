from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Base"])
def read_root():
    return {"message": "Welcome to the Base FastAPI App!"}

