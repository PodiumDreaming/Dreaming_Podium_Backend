from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from ..database import Models, crud
from ..database.conn import get_db
from ..util import create_api_token


router = APIRouter(
    tags=["Apple"],
    dependencies=[],
)


# Register new user
def sign_in(data: dict, db):
    if 'user' in data:
        user_id = "AP" + data['user']
        try:
            # check if user is already registered.
            user = crud.read_user(db=db, user_id=user_id)
            if user is not None:
                return user.user_id, user.password

            reg_date = datetime.now(tz=timezone.utc).astimezone()
            acc_type = "APPLE"
            token = create_api_token(user_id)

            # Make user model.
            user_data = {
                "user_id": user_id,
                "register_date": reg_date,
                "acc_type": acc_type,
            }
            user_db = Models.UserFull(**user_data, password=token)
            crud.create_user(db=db, user=user_db)
            return user_id, token

        except SQLAlchemyError:
            return {"Error": "SQL operation failed."}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user.")


@router.post("/create_user")
async def register(res: dict, db: Session = Depends(get_db)):
    """
    Login with Appel Account.\n
    :param res: Response you received from Apple server.\n
    :param db: This field is not required.\n
    :return:  \n
    """
    user_id, token = sign_in(data=res, db=db)
    return {"user_id": user_id, "API_Token": token}
