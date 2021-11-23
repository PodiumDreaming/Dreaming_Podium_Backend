from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import crud, Models
from app.database.conn import get_db
from app.database.Models import Profile
from app.util import convert_date

router = APIRouter(
    prefix="/profile",
    tags=["프로필"],
    dependencies=[],
)


@router.get("/read_profile/{user_id}")
async def get_profile(user_id: str, db: Session = Depends(get_db)):
    """
        API to get user's profile.\n
        :param user_id: user's user_id.\n
        :param db: This field is not required.
    """
    profile = crud.read_profile(db=db, user_id=user_id)
    if profile is None:
        default = {
            "user_id": user_id,
            "name": None,
            "gender": None,
            "birthday": None,
            "team": None,
            "field": None,
            "profile_image": None,
        }
        return default
    else:
        return {
            "user_id": user_id,
            "name": profile.name,
            "gender": profile.gender,
            "birthday": profile.birthday,
            "team": profile.team,
            "field": profile.field,
            "profile_image": profile.profile_image,
        }


@router.post("/create_profile/{user_id}")
async def make_profile(user_id: str,
                       name: str,
                       gender: str,
                       birthday: str,
                       team: str,
                       field: str,
                       db: Session = Depends(get_db)):
    """
        API to make new user's profile.\n
        Profile image should be updated later using 'update_profile' API.\n
        :param user_id: user's user_id.\n
        Profile attributes;\n
        :param name: "이름",\n
        :param gender: "성별",\n
        :param birthday: "생년월일" -> 'Sun 01 01 2021',\n
        :param team: "소속 (팀)",\n
        :param field: "종목",\n
        :param db: This field is not required.
        """
    old = crud.read_profile(db=db, user_id=user_id)
    if old is None:
        try:
            d = convert_date(birthday).get("date")
            default = {
                "user_id": user_id,
                "name": name,
                "gender": gender,
                "birthday": d,
                "team": team,
                "field": field,
                "profile_image": None,
            }
            record = crud.create_profile(db=db, profile=Models.Profile(**default))
        except SQLAlchemyError:
            return {"Status": "DB error."}
        except KeyError:
            return {"Status": "KeyError: could not find key from the given data."}
        else:
            return {"Status": "200OK",
                    "profile": record}
    else:
        return {"Status": "Profile already exists.",
                "profile": old}


@router.post("/update_profile/{user_id}")
async def update_profile(user_id: str, keyword: str, content: str, db: Session = Depends(get_db)):
    """
    API to update user's profile.\n
    :param user_id: user's user_id.\n
    :param keyword: Keyword includes:\n
        name: 이름\n
        gender: 성별\n
        birthday: 생년월일\n
        team: 소속 (팀)\n
        field: 종목\n
    :param content: updating content.\n
    :param db: This field is not required.
    """
    if keyword not in ["name", "gender", "birthday", "team", "field"]:
        return {"Keyword Error": "Check keyword."}
    else:
        profile = crud.read_profile(db=db, user_id=user_id)
        if profile is None:
            return {"Error": "Couldn't find requested user."}
        if keyword == "name":
            new_profile = Profile(user_id=user_id,
                                  name=content,
                                  gender=profile.gender,
                                  birthday=profile.birthday,
                                  team=profile.team,
                                  field=profile.field,
                                  profile_image=profile.profile_image)
        elif keyword == "gender":
            new_profile = Profile(user_id=user_id,
                                  name=profile.name,
                                  gender=content,
                                  birthday=profile.birthday,
                                  team=profile.team,
                                  field=profile.field,
                                  profile_image=profile.profile_image)
        elif keyword == "birthday":
            d = convert_date(content).get("date")
            new_profile = Profile(user_id=user_id,
                                  name=profile.name,
                                  gender=profile.gender,
                                  birthday=d,
                                  team=profile.team,
                                  field=profile.field,
                                  profile_image=profile.profile_image)
        elif keyword == "team":
            new_profile = Profile(user_id=user_id,
                                  name=profile.name,
                                  gender=profile.gender,
                                  birthday=profile.birthday,
                                  team=content,
                                  field=profile.field,
                                  profile_image=profile.profile_image)
        else:
            new_profile = Profile(user_id=user_id,
                                  name=profile.name,
                                  gender=profile.gender,
                                  birthday=profile.birthday,
                                  team=profile.team,
                                  field=content,
                                  profile_image=profile.profile_image)
        try:
            crud.update_profile(db=db, profile=new_profile)
        except SQLAlchemyError as sql:
            return {"Status": "DB error.",
                    "Detail": sql}
        else:
            return {"Status": "200OK",
                    "profile": new_profile}
