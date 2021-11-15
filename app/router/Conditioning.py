from fastapi import APIRouter, Depends, HTTPException
from ..database import Models, crud
from ..database.conn import get_db
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from ast import literal_eval


router = APIRouter(
    prefix="/condition",
    tags=["컨디셔닝"],
    dependencies=[],
)


@router.get("/testCR")
async def write(db: Session = Depends(get_db)):
    data = {
        "user_id": "1951543508",
        "written": date.today(),
        "content": {
            "부상": None,
            "기분": "보통",
        }
    }
    test_data = Models.Condition(**data)
    return crud.create_cr(cr=test_data, db=db)


@router.get("/read")
async def read(user_id: str, wdate: date, number: Optional[int] = 1, db: Session = Depends(get_db)):
    record = crud.read_cr(db, user_id, wdate, number)
    if record is None:
        raise HTTPException(status_code=404, detail="Could not find user")
    return record


def write_crecord(record: Models.Condition, db: Session = Depends(get_db)):
    return crud.create_cr(cr=record, db=db)


@router.post("/update")
async def update_record(user_id: str, wdate: date, content, db: Session = Depends(get_db)):
    return crud.update_cr(db=db,
                          user_id=user_id,
                          wdate=wdate,
                          content=content)


@router.delete("/delete")
async def delete_record(user_id: str, wdate: date, db: Session = Depends(get_db)):
    if not crud.delete_cr(db=db, user_id=user_id, wdate=wdate):
        raise HTTPException(status_code=404, detail="Could not find user")
    else:
        return {"status": "200"}
