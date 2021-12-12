from fastapi import APIRouter, Depends, Header, HTTPException, status
from ..database import Models, crud
from app.database.conn import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Union
from ..util import convert_date, token_verification, create_api_token


router = APIRouter(
    prefix="/record",
    tags=["Record"],
    dependencies=[],
)


# Create default training record.
def initialize_t(user_id, wdate, db):
    try:
        obj = crud.read_objective(db=db, user_id=user_id)
        if obj:
            routines = {}
            for routine in obj.routines:
                routines.update({routine: False})
        else:
            routines = None
        tr = {
            "user_id": user_id,
            "written": wdate,
            "content": {
                "train_detail": {"content": None},
                "routines": routines,
                "success": {"content": None, "image": []},
                "failure": {"content": None, "image": []},
            },
            "feedback": None,
        }
        crud.create_tr(tr=Models.Training(**tr), db=db)
    except SQLAlchemyError as sql:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"SQL operation failed.": sql},)


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
    try:
        crud.create_cr(cr=Models.Condition(**cr), db=db)
    except SQLAlchemyError as sql:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"SQL operation failed.": sql},
        )


# Create/overwrites tr/cr record of given date.
@router.post("/write/{user_id}")
async def write(user_id: str, wdate: str, key_type: str, content: Union[str, dict, List[str], List[dict]],
                db: Session = Depends(get_db),
                token=Header(..., title="API_Token")):
    """
    :param db: Connection to database. This field is not needed.\n
    :param user_id: str\n
     - User_id of the owner of the record.\n
    :param wdate: str\n
     - Date of the record. Must be something like 'Fri Nov 05 2021'\n
    :param key_type: str\n
     - Identifier of Updating part of the record. key_type must be one of:\n
        "train_detail"\n
        "routines"\n
        "success"\n
        "failure"\n
        "feedback"\n
        "mind"\n
        "physical"\n
        "injury"\n
    :param content: Writing content\n
    content: Updating value.\n
    Type of content should be one of [str, dict, list[str], list[dict]]\n
    :param token: API_Token you received when you registered in.\n
    :return: 200 Ok on Success.\n
    """
    if not token_verification(token=token, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    try:
        d = convert_date(wdate).get("date")
        if d is None:
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Value Error"
        )

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

        # training data update
        if key_type == "train_detail":
            detail = {"content": content}
            tr.content["train_detail"] = detail

        elif key_type == "routines":
            tr.content["routines"] = content.get("content")

        elif key_type == "success":
            url = tr.content.get("success").get("image")
            success = {"content": content, "image": url}
            tr.content["success"] = success

        elif key_type == "failure":
            url = tr.content.get("failure").get("image")
            failure = {"content": content, "image": url}
            tr.content["failure"] = failure

        elif key_type == "feedback":
            tr.feedback = content

        # conditioning data update
        elif key_type == "mind":
            cr.content["mind"] = content.get("content")

        elif key_type == "physical":
            cr.content["physical"] = content.get("content")

        elif key_type == "injury":
            cr.content["injury"] = content.get("content")

        crud.update_tr(db=db, user_id=user_id, content=tr.content, wdate=d, feedback=tr.feedback)
        crud.update_cr(db=db, user_id=user_id, content=cr.content, wdate=d)

    except SQLAlchemyError as sql:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={"SQL operation failed.": sql},
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"KeyError": "key probably doesn't exist."}
        )
    return {"status": status.HTTP_201_CREATED}


# Read tr/cr record of given user_id and given date.
@router.get("/read/{user_id}")
async def read(user_id: str, wdate: str, db: Session = Depends(get_db), token=Header(..., title="API_Token")):
    """

    :param user_id: User_id of the owner of the record.\n
    :param wdate: Date of the record. Must be something like 'Fri Nov 05 2021'\n
    :param db: This field is not required.\n
    :param token: API_Token you received when you registered in.\n
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
    # verify API_Token
    if not token_verification(token=token, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    try:
        # check if user exists
        user = crud.read_user(db=db, user_id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found",
            )
    except SQLAlchemyError as sql:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"SQL operation failed.": sql},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Unexpected Error": e}
        )
    else:
        try:
            d = convert_date(wdate).get("date")

            tr = crud.read_tr(user_id=user_id, wdate=d, db=db, number=1)
            training = {
                "train_detail": {"content": None},
                "routines": None,
                "success": {"content": None, "image": []},
                "failure": {"content": None, "image": []},
            }
            # set training return message if record doesn't exist.
            if len(tr) == 0 or tr is None:
                obj = crud.read_objective(db=db, user_id=user_id)
                if obj:
                    routines = obj.routines
                    if routines:
                        tr_routine = {}
                        for routine in routines:
                            tr_routine.update({routine: False})
                        training["routines"] = tr_routine
                feedback = None
            else:
                training = tr[0].content
                feedback = tr[0].feedback

            cr = crud.read_cr(user_id=user_id, wdate=d, db=db, number=1)
            # set training return message if record doesn't exist.
            if len(cr) == 0 or cr is None:
                conditioning = {
                    "mind": [],
                    "physical": [],
                    "injury": [],
                }
            else:
                conditioning = cr[0].content
            # put together into one response object
            res = {
                "date": wdate,
                "noteContentGroup": {
                    "training": training,
                    "feedback": feedback,
                    "conditioning": conditioning,
                }
            }
            return res
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check if user_id has valid value or date is in right format. Example: 'Fri Nov 05 2021'",
            )


# API for testing
@router.get("/token_test")
async def test(user_id: str, token=Header(..., title="API_Token")):
    if not token_verification(token, user_id):
        return {"Verification": "Failure"}
    else:
        return {"Verification": "Success"}


@router.get("/my_token")
async def get_token(user_id: str):
    token = create_api_token(user_id)
    return token
