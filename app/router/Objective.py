from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import crud
from app.database.conn import get_db
from datetime import date
from typing import List
from ..database import Models


router = APIRouter(
    prefix="/objective",
    tags=["목표설정"],
    dependencies=[],
)


def sync_obj(user_id: str, routines, db: Session):
    # check if there is today's record.
    today = date.today()
    today_record = crud.read_tr(db=db, user_id=user_id, wdate=today, number=1)
    # if so, synchronize updated routine data.
    if len(today_record) > 0:
        tr = today_record[0]
        new_r = {}
        for routine in routines:
            new_r.update({routine: False})
        tr.content["routines"] = new_r
        crud.update_tr(db=db, user_id=user_id, wdate=today, content=tr.content, feedback=tr.feedback)


@router.post("/create_objectives")
async def create_objective(content: Models.Objectives, db: Session = Depends(get_db)):
    """
    API to create or update objectives of a user.\n
    :param content: Attributes, all in list form.\n
        "objectives": "목표"\n
        "requirements": "자질"\n
        "efforts": "노력"\n
        "routines": "루틴"\n
    :param db: this field is not required.\n
    :return: 200OK on success with updated objectives.\n
    """
    try:
        new = {
            "user_id": content.user_id,
            "objectives": content.objectives,
            "requirements": content.requirements,
            "efforts": content.efforts,
            "routines": content.routines,
        }
        obj = crud.read_objective(db=db, user_id=content.user_id)
        if obj is None:
            record = crud.create_objective(db=db, obj=Models.Objectives(**new))
        else:
            # This will overwrite all attributes.
            crud.update_objective(db=db, obj=Models.Objectives(**new))
            record = new
            # synchronize data with record.
            sync_obj(user_id=content.user_id, routines=content.routines, db=db)

        return {"Status": "200OK",
                "objective": record}
    except SQLAlchemyError as sql:
        print(sql)
        return {"Status": "DB error.",
                "Detail": sql}
    except KeyError:
        return {"Status": "KeyError: could not find key from the given data."}


@router.post("/update_objectives/{user_id}")
async def update_objective(user_id: str, keyword: str, content: List[str], db: Session = Depends(get_db)):
    """
    API to update specific attribute of an objective of a user.\n
    :param user_id: user_id of user.\n
    :param keyword: attribute to change.\n
        user_id: str\n
        objectives: List[str] 목표\n
        requirements: List[str] 자질\n
        efforts: List[str] 노력\n
        routines: List[str] 루틴\n
    :param content: new value. Must be in List;\n
    :param db: this field is not required.\n
    :return: 200OK on success with updated objectives.\n
    """
    if keyword not in ["objectives", "requirements", "efforts", "routines"]:
        return {"Keyword Error": "Check keyword."}
    try:
        old = crud.read_objective(db=db, user_id=user_id)
        if old is None:
            return {"Error": "Couldn't find requested user."}
        else:
            if keyword == "objectives":
                new = Models.Objectives(
                    user_id=user_id,
                    objectives=content,
                    requirements=old.requirements,
                    efforts=old.efforts,
                    routines=old.routines)

            elif keyword == "requirements":
                new = Models.Objectives(
                    user_id=user_id,
                    objectives=old.objectives,
                    requirements=content,
                    efforts=old.efforts,
                    routines=old.routines)

            elif keyword == "efforts":
                new = Models.Objectives(
                    user_id=user_id,
                    objectives=old.objectives,
                    requirements=old.requirements,
                    efforts=content,
                    routines=old.routines)

            else:
                # routines
                new = Models.Objectives(
                    user_id=user_id,
                    objectives=old.objectives,
                    requirements=old.requirements,
                    efforts=old.efforts,
                    routines=content)
                # synchronize data with record.
                sync_obj(user_id=user_id, routines=content, db=db)

            crud.update_objective(db=db, obj=new)

    except SQLAlchemyError:
        return {"Status": "DB error."}
    except KeyError:
        return {"Status": "KeyError: could not find key from the given data."}
    else:
        return {"Status": "200OK",
                "profile": new}


@router.get("/read_objectives/{user_id}")
async def get_objective(user_id: str, db: Session = Depends(get_db)):
    """
        API to get user's objectives.\n
        :param user_id: user's user_id.\n
        :param db: This field is not required.
    """
    obj = crud.read_objective(db=db, user_id=user_id)
    if obj is None:
        default = {
            "user_id": user_id,
            "objectives": [],
            "requirements": [],
            "efforts": [],
            "routines": [],
        }
        return default
    else:
        return obj
