from . import Models, Tables
from sqlalchemy.orm import Session
from datetime import datetime, date


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
                              team=user.team, field=user.field, email=user.email, register_date=user.register_date,
                              acc_type=user.acc_type, password=user.password, refresh_token=user.refresh_token)
    db.add(user_record)
    db.commit()
    db.refresh(user_record)


def read_user(db: Session, user_id: str):
    return db.query(Tables.User).filter(Tables.User.user_id == user_id).first()


def update_user(db: Session, user: Models.UserFull):
    updates = db.query(Tables.User).filter(Tables.User.user_id).update(user)
    return True


def delete_user(db: Session, user_id: str):
    user = db.query(Tables.User).filter(Tables.User.user_id == user_id).first()
    if user is None:
        return False
    else:
        db.delete(user)
        db.commit()
    return True


def create_tr(db: Session, tr: Models.Training):
    """
    data = tr.dict()
    user_id = data["user_id"]
    written = data["written"]
    last_modified = data["last_modified"]
    content = data["content"]
    feedback = data["feedback"]
    :return:
    """
    record = Tables.TR(user_id=tr.user_id, written=tr.written, last_modified=tr.last_modified, content=tr.content,
                       feedback=tr.feedback)
    db.add(record)
    db.commit()
    db.refresh(record)


def create_cr(db: Session, cr: Models.Condition):
    """
        data = tr.dict()
        user_id = data["user_id"]
        written = data["written"]
        last_modified = data["last_modified"]
        content = data["content"]
        feedback = data["feedback"]
        :return:
        """
    record = Tables.CR(user_id=cr.user_id, written=cr.written, last_modified=cr.last_modified, content=cr.content)
    db.add(record)
    db.commit()
    db.refresh(record)


def read_tr(db: Session, user_id: str, wdate: date):
    return db.query(Tables.TR).filter(Tables.TR.user_id == user_id and
                                      Tables.TR.written == wdate).first()


def read_cr(db: Session, user_id: str, wdate: date):
    return db.query(Tables.CR).filter(Tables.CR.user_id == user_id and
                                      Tables.CR.written == wdate).first()


def update_tr():
    pass


def update_cr():
    pass


def delete_tr():
    pass


def delete_cr():
    pass
