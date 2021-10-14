from ..Model import User, UserFull


def create_user(user: UserFull):
    data = user.dict()
    name = data["name"]
    gender = data["gender"]
    birthday = data["birthday"]
    team = data["team"]
    field = data["field"]
    email = data["email"]
    register_date = data["register_data"]
    acc_type = data["acc_type"]
    # a command to create a record in db(params)
    return {"User": user}


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
