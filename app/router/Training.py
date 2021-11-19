from fastapi import APIRouter, Depends, HTTPException
from ..database import Models, crud
from ..database.conn import get_db
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional


router = APIRouter(
    prefix="/train",
    tags=["트레이닝"],
    dependencies=[],
)


@router.get("/testTR")
async def write(db: Session = Depends(get_db)):
    data = {
        "user_id": "KA1951543508",
        "written": date.today(),
        "content": {
            "train_detail": "jogging",
            "routines": {"routine1": "done",
                            "routine2": "done"},
            "success": "time reduce",
            "failure": "breathe control",
        },
        "feedback": "Do better"
    }
    test_data = Models.Training(**data)
    return crud.create_tr(tr=test_data, db=db)


@router.get("/read")
async def read(user_id: str, wdate: date = date.today(), number: Optional[int] = 1, db: Session = Depends(get_db)):
    record = crud.read_tr(db, user_id, wdate, number)
    if record is None:
        raise HTTPException(status_code=404, detail="Could not find user")
    return record


def write_trecord(record: Models.Training, db):
    return crud.create_tr(tr=record, db=db)


@router.post("/update")
async def update_record(user_id: str, content, wdate: date, feedback: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.update_tr(db=db,
                          user_id=user_id,
                          wdate=wdate,
                          content=content,
                          feedback=feedback)

'''
@router.delete("/delete")
async def delete_record(user_id: str, wdate: date, db: Session = Depends(get_db)):
    if not crud.delete_tr(db=db, user_id=user_id, wdate=wdate):
        raise HTTPException(status_code=404, detail="Could not find user")
    else:
        return {"status": "200"}
'''