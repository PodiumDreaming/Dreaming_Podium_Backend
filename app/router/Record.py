from fastapi import APIRouter, Depends, File, UploadFile
from typing import Optional
from datetime import date, datetime, timezone
import json
from ..database import Models
from ..router import Training, Conditioning
from app.database.conn import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/record",
    tags=["기록"],
    dependencies=[],
)


@router.post("/write/{user_id}")
async def write(user_id, record=None, db: Session = Depends(get_db)):
    sample = {
        # 쓰인 날짜
        "date": 'Fri Nov 05 2021',
        # "date": "2021-11-15",
        # [트레이닝 파트 글 목록]
        "noteContentGroup": {
            "training": {
                "train_detail": "노트내용",
                "routines": {"routine_name1": "done",
                             "routine_name2": "done"},
                "success": "뭔가 잘한것",
                "failure": "뭔가 못한것",
            },
            "feedback": "피드백 내용",
            "conditioning": {
                "mind": ['정신이 번쩍'],
                "physical": [],
                "injury": []
            },
        }
    }
    if record is None:
        record = sample

    record_date = record.get("date")
    d = datetime.strptime(record_date, '%a %b %d %Y').date()
    contents = record.get("noteContentGroup")

    tr = contents.get("training")
    feedback = contents.get("feedback")
    TR = {
        "user_id": user_id,
        "written": d,
        "content": tr,
        "feedback": feedback
    }
    training_record = Models.Training(**TR)
    Training.write_trecord(training_record, db=db)

    cr = contents.get("conditioning")
    CR = {
        "user_id": user_id,
        "written": d,
        "content": cr,
    }
    conditioning_record = Models.Condition(**CR)
    Conditioning.write_crecord(conditioning_record, db=db)

    return {"status": "200OK"}
