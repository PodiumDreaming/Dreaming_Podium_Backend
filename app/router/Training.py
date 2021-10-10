from fastapi import APIRouter

router = APIRouter(
    prefix="/train",
    tags=["트레이닝"],
    dependencies=[],
)