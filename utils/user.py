users = {}

class User:
    id = 0
    name = ""
    phone = ""
    email = ""
    sex = ""
    photo = 0

    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name

def add_user(id, name):
    users[str(id)] = User(id, name)
