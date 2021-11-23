from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import crud, Models
from app.database.conn import get_db
from ..util import simple_parser, complex_parser


router = APIRouter(
    prefix="/objective",
    tags=["목표설정"],
    dependencies=[],
)


@router.post("/create_objectives/{user_id}")
async def create_objective(user_id: str, objectives, requirements, efforts, routines, db: Session = Depends(get_db)):
    """
    API to create or update objectives of a user.\n
    :param user_id: user_id of user.\n
    :param: attributes, all in list form.\n
        "objectives": "목표"\n
        "requirements": "자질"\n
        "efforts": "노력"\n
        "routines": "루틴"\n
    :param db: this field is not required.\n
    :return: 200OK on success with updated objectives.\n
    """
    try:
        new = {
            "user_id": user_id,
            "objectives": objectives,
            "requirements": requirements,
            "efforts": efforts,
            "routines": routines,
        }
        obj = crud.read_objective(db=db, user_id=user_id)
        if obj is None:
            record = crud.create_objective(db=db, obj=Models.Objectives(**new))
        else:
            # This will overwrite all attributes.
            crud.update_objective(db=db, obj=Models.Objectives(**new))
            record = new

    except SQLAlchemyError as sql:
        return {"Status": "DB error.",
                "Detail": sql}
    except KeyError:
        return {"Status": "KeyError: could not find key from the given data."}
    else:
        return {"Status": "200OK",
                "objective": record}


@router.post("/update_objectives/{user_id}")
async def update_objective(user_id: str, keyword: str, content, db: Session = Depends(get_db)):
    """
    API to update specific attribute of an objective of a user.\n
    :param user_id: user_id of user.\n
    :param keyword: attribute to change.\n
        objectives: 목표\n
        requirements: 자질\n
        efforts: 노력\n
        routines: 루틴\n
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
                new = Models.Objectives(
                    user_id=user_id,
                    objectives=old.objectives,
                    requirements=old.requirements,
                    efforts=old.efforts,
                    routines=content)
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
        objectives = simple_parser(obj.objectives)
        requirements = simple_parser(obj.requirements)
        efforts = simple_parser(obj.efforts)
        routines = simple_parser(obj.routines)
        return {
            "user_id": user_id,
            "objectives": objectives,
            "requirements": requirements,
            "efforts": efforts,
            "routines": routines,
        }