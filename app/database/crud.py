from . import Models, Tables
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone


def create_user(db: Session, user: Models.UserFull):
    # a command to create a record in db(params)

    user_record = Tables.User(user_id=user.user_id, name=user.name, gender=user.gender, birthday=user.birthday,
                              team=user.team, field=user.field, email=user.email, register_date=user.register_date,
                              acc_type=user.acc_type, password=user.password, refresh_token=user.refresh_token)
    db.add(user_record)
    db.commit()
    db.refresh(user_record)
    return user_record


def read_user(db: Session, user_id: str):
    return db.query(Tables.User).filter(Tables.User.user_id == user_id).first()


def update_user(db: Session, user: Models.UserFull):
    user_info = db.query(Tables.User).filter(Tables.User.user_id).first()
    if user_info is None:
        return False
    else:
        user_info.name = user.name
        user_info.gender = user.gender
        user_info.birthday = user.birthday
        user_info.team = user.team
        user_info.field = user.field
        user_info.email = user.email
        user_info.refresh_token = user.refresh_token

        db.commit()
        return True


def delete_user(db: Session, user_id: str):
    user = db.query(Tables.User).filter(Tables.User.user_id == user_id).first()
    if user is None:
        return False
    else:
        db.delete(user)
        db.commit()
        return True


def create_tr(tr: Models.Training, db: Session):
    record = Tables.TR(user_id=tr.user_id, written=tr.written, last_modified=tr.last_modified, content=tr.content,
                       feedback=tr.feedback)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_cr(cr: Models.Condition, db: Session):
    record = Tables.CR(user_id=cr.user_id, written=cr.written, last_modified=cr.last_modified, content=cr.content)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def read_tr(db: Session, user_id: str, wdate: date, number: int):
    return db.query(Tables.TR).filter(Tables.TR.user_id == user_id,
                                      Tables.TR.written == wdate).limit(number).all()


def read_cr(db: Session, user_id: str, wdate: date, number: int):
    return db.query(Tables.CR).filter(Tables.CR.user_id == user_id,
                                      Tables.CR.written == wdate).limit(number).all()


def update_tr(db: Session, user_id: str, wdate: date, content, feedback: str):
    record = db.query(Tables.TR).filter(Tables.TR.user_id == user_id,
                                        Tables.TR.written == wdate).first()
    if record is None:
        return False
    else:
        now = datetime.now(tz=timezone.utc).astimezone()
        record.last_modified = now
        record.content = content
        record.feedback = feedback
        db.commit()
        return True


def update_cr(db: Session, user_id: str, wdate: date, content):
    record = db.query(Tables.CR).filter(Tables.CR.user_id == user_id,
                                        Tables.CR.written == wdate).first()
    if record is None:
        return False
    else:
        now = datetime.now(tz=timezone.utc).astimezone()
        record.last_modified = now
        record.content = content
        db.commit()
        return True


def delete_tr(db: Session, user_id: str, wdate: date):
    record = db.query(Tables.TR).filter(Tables.TR.user_id == user_id,
                                        Tables.TR.written == wdate).first()
    if record is None:
        return False
    else:
        db.delete(record)
        db.commit()
        return True


def delete_cr(db: Session, user_id: str, wdate: date):
    record = db.query(Tables.CR).filter(Tables.CR.user_id == user_id,
                                        Tables.CR.written == wdate).first()
    if record is None:
        return False
    else:
        db.delete(record)
        db.commit()
        return True


def save_img(db: Session, name, data):
    record = Tables.image(img_name=name, img_data=data)
    db.add(record)
    db.commit()
    db.refresh(record)


def read_img(db: Session):
    return db.query(Tables.image).first()
