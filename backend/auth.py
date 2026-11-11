import json
import bcrypt
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "users.json"
)


def load_users():

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def register_user(name, email, password):

    users = load_users()

    for user in users:

        if user["email"].lower() == email.lower():
            return "Email already registered"

    if not name.strip() or not email.strip() or len(password) < 8:
        return "Enter valid details and a password of at least 8 characters"

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = {
        "id": "U" + str(len(users) + 1).zfill(3),
        "name": name,
        "email": email.lower(),
        "password": hashed_password
    }

    users.append(new_user)

    save_users(users)

    return "Registration successful"


def login_user(email, password):

    users = load_users()

    for user in users:

        if user["email"].lower() == email.lower():

            stored_password = user["password"].encode("utf-8")

            if bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password
            ):
                return "Login successful"

            return "Incorrect password"

    return "User not found"


if __name__ == "__main__":

    choice = input("1. Register\n2. Login\nChoose: ")

    if choice == "1":

        name = input("Enter name: ")
        email = input("Enter email: ")
        password = input("Enter password: ")

        print(register_user(name, email, password))

    elif choice == "2":

        email = input("Enter email: ")
        password = input("Enter password: ")

        print(login_user(email, password))

    else:
        print("Invalid choice")