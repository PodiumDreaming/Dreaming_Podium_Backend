from fastapi import APIRouter, Depends
from ..database import Models, crud
from app.database.conn import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Union
from ..util import simple_parser, complex_parser, convert_date

router = APIRouter(
    prefix="/record",
    tags=["기록"],
    dependencies=[],
)


# Create default training record.
def initialize_t(user_id, wdate, db):
    tr = {
        "user_id": user_id,
        "written": wdate,
        "content": {
            "train_detail": None,
            "routines": [],
            "success": {"content": None, "image": None},
            "failure": {"content": None, "image": None},
        },
        "feedback": None,
    }
    crud.create_tr(tr=Models.Training(**tr), db=db)


# Create default conditioning record.
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


# Create/overwrites tr/cr record of given date.
@router.post("/write/{user_id}")
async def write(user_id: str, wdate: str, key_type: str, content: Union[str, dict, List[str], List[dict]],
                db: Session = Depends(get_db)):
    """
    :param db: Connection to database. This field is not needed.\n
    :param user_id: str\n
     - User_id of the owner of the record.\n
    :param wdate: str\n
     - Date of the record. Must be something like 'Fri Nov 05 2021'\n
    :param key_type: str\n
     - Identifier of Updating part of the record. key_type must be one of:\n
        "train_detail" :
        "routines" :
        "success" :
        "failure":
        "feedback":
        "mind"
        "physical"
        "injury"\n
    :param content: Writing content\n
    content: Updating value.\n
    Type of content should be one of [str, dict, list[str], list[dict]]
    :return: 200Ok on Success.\n
    """
    try:
        d = convert_date(wdate).get("date")
        if d is None:
            raise ValueError
        if key_type in ["mind", "physical", "injury"]:
            if type(content) != list:
                raise ValueError
    except ValueError:
        return {"Error": "Invalid value"}

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

        # training data
        if key_type == "train_detail":
            detail = {"content": content}
            tr.content["train_detail"] = detail
        elif key_type == "routines":
            tr.content["routines"] = content
        elif key_type == "success":
            url = tr.content.get("success").get("image")
            success = {"content": content, "image": url}
            tr.content["success"] = success
        elif key_type == "failure":
            url = tr.content.get("failure").get("image")
            failure = {"content": content, "image": url}
            tr.content["failure"] = failure
        elif key_type == "feedback":
            feedback = {"content": content}
            tr.content["train_detail"] = feedback
        # conditioning data
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


# Read tr/cr record of given user_id and given date.
@router.get("/read/{user_id}")
async def read(user_id: str, wdate: str, db: Session = Depends(get_db)):
    """

    :param user_id: User_id of the owner of the record.\n
    :param wdate: Date of the record. Must be something like 'Fri Nov 05 2021'\n
    :param db: This field is not required.\n
    :return: User record of given date.
    """
    """
    sample = {\n
        "wdate": 'Fri Nov 15 2021',\n
        "noteContentGroup": {\n
            "training": {\n
                "train_detail": "노트내용",\n
                "routines": {"routine_name1": "done",\n
                             "routine_name2": "done"},\n
                "success": "뭔가 잘한것",\n
                "failure": "뭔가 못한것",\n
            },\n
            "feedback": "피드백 내용",\n
            "conditioning": {\n
                "mind": ['정신이 번쩍'],\n
                "physical": [],\n
                "injury": []\n
            },\n
        }\n
    }\n
    """
    try:
        user = crud.read_user(db=db, user_id=user_id)
        if user is None:
            return {"user not found"}
    except SQLAlchemyError:
        return {"Error": "Operation Failed."}
    except Exception as e:
        return {"Error:": e}
    else:
        try:
            d = convert_date(wdate).get("date")

            tr = crud.read_tr(user_id=user_id, wdate=d, db=db, number=1)
            # set default return message if record doesn't exist.
            if len(tr) == 0 or tr is None:
                training = {
                    "train_detail": {"content": None},
                    "routines": [],
                    "success": {"content": None, "image": None},
                    "failure": {"content": None, "image": None},
                }
                feedback = {"content": None}
            else:
                training = tr[0].content
                feedback = tr[0].feedback
            training["feedback"] = feedback

            cr = crud.read_cr(user_id=user_id, wdate=d, db=db, number=1)
            # set default return message if record doesn't exist.
            if len(cr) == 0 or cr is None:
                conditioning = {
                    "mind": [],
                    "physical": [],
                    "injury": [
                        {
                            "injuryDirection": None,
                            "injurySection": None,
                            "InjuryForm": None,
                            "painData": None,
                            "interruptData": None,
                            "injuryMemo": None,
                         }
                    ],
                }
            else:
                conditioning = cr[0].content

            res = {
                "date": wdate,
                "noteContentGroup": {
                    "training": training,
                    "conditioning": conditioning,
                }
            }
            return res
        except (TypeError, ValueError):
            return {"Check if user_id has valid value or date is in right format. Example: 'Fri Nov 05 2021'"}
