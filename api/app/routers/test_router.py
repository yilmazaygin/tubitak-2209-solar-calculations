from fastapi import APIRouter


router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/")
def test_endpoint():
    return {"message": "This is a test endpoint"}
