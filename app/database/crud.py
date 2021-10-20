from . import Models, Tables
from sqlalchemy.orm import Session


def create_user(db: Session, user: Models.UserFull):
    """
    data = user.dict()
    name = data["name"]
    gender = data["gender"]
    birthday = data["birthday"]
    team = data["team"]
    field = data["field"]
    email = data["email"]
    register_date = data["register_data"]
    acc_type = data["acc_type"]
    """

    # a command to create a record in db(params)

    user_record = Tables.User(user_id=user.user_id, name=user.name, gender=user.gender, birthday=user.birthday,
                              team=user.team, field=user.field, email=user.email, reg_date=user.register_date,
                              acc_type=user.acc_type, password=user.password, refresh_token=user.refresh_token)
    db.add(user_record)
    db.commit()
    db.refresh(user_record)


def read_user():
    pass


def update_user():
    pass


def delete_user():
    pass


def create_tr():
    pass


def create_cr():
    pass


def read_tr():
    pass


def read_cr():
    pass


def update_tr():
    pass


def update_cr():
    pass


def delete_tr():
    pass


def delete_cr():
    pass
