from fastapi import APIRouter

router = APIRouter(prefix="/v1")


@router.get("/hello")
async def hello():
    return {"message": "hello"}


@router.get("/search")
async def search():
    return {"results": []}


@router.post("/export")
async def export():
    return {"status": "started"}
