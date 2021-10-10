from fastapi import APIRouter

router = APIRouter(
    prefix="/condition",
    tags=["컨디셔닝"],
    dependencies=[],
)