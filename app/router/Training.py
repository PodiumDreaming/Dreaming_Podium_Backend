from fastapi import APIRouter, Depends, HTTPException
from ..database import Models, crud
from ..database.conn import get_db
from sqlalchemy.orm import Session
from datetime import datetime, date

router = APIRouter(
    prefix="/train",
    tags=["트레이닝"],
    dependencies=[],
)


@router.get("/testTR")
async def write(db: Session = Depends(get_db)):
    data = {
        "user_id": "1951543508",
        "written": '2021-10-26',
        "last_modified": None,
        "content": {
            "훈련내용": "달리기",
            "루틴": {"루틴1": "done",
                   "루틴2": "done"},
            "잘한점": "시간단축",
            "목한점": "호흡조절",
        }
    }
    test_data = Models.Training(**data)
    crud.create_tr(db=db, tr=test_data)
    return test_data


@router.get("/getTR")
async def read(user_id: str, wdate: date, db: Session = Depends(get_db)):
    record = crud.read_tr(db, user_id, wdate)
    if record is None:
        raise HTTPException(status_code=404, detail="Could not find user")
    return record
