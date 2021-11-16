from fastapi import APIRouter, Depends, File, UploadFile
from typing import Optional
from datetime import datetime

from ..database import Models, crud
from ..router import Training, Conditioning
from app.database.conn import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(
    prefix="/record",
    tags=["기록"],
    dependencies=[],
)


def convert_date(date):
    try:
        d = datetime.strptime(date, '%a %b %d %Y').date()
        detail = {"status": "200OK"}
    except KeyError:
        d = None
        detail = {"KeyError": "Check record has valid keys."}
    except (TypeError, ValueError):
        d = None
        detail = {"Type/Value Error": "Check if date has valid value or is in right format. Example: 'Fri Nov 05 2021'"}
    except Exception:
        d = None
        detail = {"Exception": "Could not handle data. Check if data is valid."}
    return {"date": d, "detail": detail}


def initialize_t(user_id, wdate, db):
    tr = {
        "user_id": user_id,
        "written": wdate,
        "content": {
            "train_detail": None,
            "routines": None,
            "success": {"content": None, "image": None},
            "failure": {"content": None, "image": None},
        },
        "feedback": None,
    }
    crud.create_tr(tr=Models.Training(**tr), db=db)


def initialize_c(user_id, wdate, db):
    cr = {
        "user_id": user_id,
        "written": wdate,
        "content": {
            "mind": [],
            "physical": [],
            "injury": [],
        }
    }
    crud.create_cr(cr=Models.Condition(**cr), db=db)


@router.post("/write/{user_id}")
async def write(user_id, wdate, key_type, content, db: Session = Depends(get_db)):
    """
    :param db: Connection to database. This field is not needed.\n
    :param user_id: User_id of the owner of the record.\n
    :param wdate: Date of the record.\n
    :param key_type: Identifier of Updating part of the record.\n
    key_type must be one of:
    "train_detail", "routines", "success", "failure", "mind", "physical", "injury"\n
    :param content: Updating value. mind/physical/injury values must be list --> e.g) ["lethargic", "Tired"].\n
    :return: 200Ok on Success.\n
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
    """

    d = convert_date(wdate).get("date")
    try:
        tr_record = crud.read_tr(db=db, user_id=user_id, wdate=d, number=1)
        cr_record = crud.read_cr(db=db, user_id=user_id, wdate=d, number=1)
        # initializing part: create record if there isn't one.
        if len(tr_record) == 0:
            initialize_t(user_id=user_id, wdate=d, db=db)
            tr_record = crud.read_tr(db=db, user_id=user_id, wdate=d, number=1)
        if len(cr_record) == 0:
            initialize_c(user_id=user_id, wdate=d, db=db)
            cr_record = crud.read_cr(db=db, user_id=user_id, wdate=d, number=1)

        # updating part
        tr = tr_record[0]
        cr = cr_record[0]
        if key_type == "train_detail":
            tr.content["train_detail"] = content
        elif key_type == "routines":
            tr.content["routines"] = content
        elif key_type == "success":
            tr.content["success"] = content
        elif key_type == "failure":
            tr.content["failure"] = content
        elif key_type == "mind":
            cr.content["mind"] = content
        elif key_type == "physical":
            cr.content["physical"] = content
        elif key_type == "injury":
            cr.content["injury"] = content

        crud.update_tr(db=db, user_id=user_id, content=tr.content, wdate=d, feedback=tr.feedback)
        crud.update_cr(db=db, user_id=user_id, content=cr.content, wdate=d)

    except SQLAlchemyError:
        return {"Error": "Error occurred while reading data."}
    except KeyError:
        return {"KeyError": "key probably doesn't exist."}
    return {"status": "200OK"}


@router.get("/get/{user_id}")
async def read(user_id, date, db: Session = Depends(get_db)):
    """
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
    """
    try:
        user = crud.read_user(db=db, user_id=user_id)
        if user is None:
            return {"user not found"}
    except SQLAlchemyError:
        return {"Error": "Operation Failed."}
    except Exception:
        pass
    else:
        try:
            d = datetime.strptime(date, '%a %b %d %Y').date()

            tr = crud.read_tr(user_id=user_id, wdate=d, db=db, number=1)
            if len(tr) == 0 or tr is None:
                training = {
                    "train_detail": None,
                    "routines": None,
                    "success": {"content": None, "image": None},
                    "failure": {"content": None, "image": None},
                }
                feedback = None
            else:
                training = tr[0].content
                feedback = tr[0].feedback

            cr = crud.read_cr(user_id=user_id, wdate=d, db=db, number=1)
            if len(cr) == 0 or cr is None:
                conditioning = {
                    "mind": [],
                    "physical": [],
                    "injury": [],
                }
            else:
                conditioning = cr[0].content

            res = {
                "date": date,
                "noteContentGroup": {
                    "training": training,
                    "feedback": feedback,
                    "conditioning": conditioning,
                }
            }
            return res
        except (TypeError, ValueError):
            return {"Check if user_id has valid value or date is in right format. Example: 'Fri Nov 05 2021'"}
