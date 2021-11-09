from fastapi import APIRouter, Depends, HTTPException
from ..database import Models, crud
from ..database.conn import get_db
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from typing import Optional

router = APIRouter(
    prefix="/train",
    tags=["트레이닝"],
    dependencies=[],
)


@router.get("/testTR")
async def write(db: Session = Depends(get_db)):
    now = datetime.now(tz=timezone.utc)
    localtime = now.astimezone()
    data = {
        "user_id": "1951543508",
        "written": localtime,
        "last_modified": localtime,
        "content": {
            "훈련내용": "달리기",
            "루틴": {"루틴1": "done",
                   "루틴2": "done"},
            "잘한점": "시간단축",
            "목한점": "호흡조절",
        },
        "feedback": "Do better"
    }
    test_data = Models.Training(**data)
    crud.create_tr(db=db, tr=test_data)
    return test_data


@router.get("/read")
async def read(user_id: str, wdate: date, number: Optional[int] = 1, db: Session = Depends(get_db)):
    record = crud.read_tr(db, user_id, wdate, number)
    if record is None:
        raise HTTPException(status_code=404, detail="Could not find user")
    return record


@router.post("/create")
async def write_record(record: Models.Training, db: Session = Depends(get_db)):
    return crud.create_tr(db=db, tr=record)


@router.post("/update")
async def update_record(user_id: str, wdate: date, content, feedback: str, db: Session = Depends(get_db)):
    return crud.update_tr(db=db,
                          user_id=user_id,
                          wdate=wdate,
                          content=content,
                          feedback=feedback)


@router.delete("/delete")
async def delete_record(user_id: str, wdate: date, db: Session = Depends(get_db)):
    if not crud.delete_tr(db=db, user_id=user_id, wdate=wdate):
        raise HTTPException(status_code=404, detail="Could not find user")
    else:
        return {"status": "200"}
