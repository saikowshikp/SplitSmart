from flask_login import login_user

from app.models.user import User


class AuthService:

    @staticmethod
    def register(name, email, password):

        existing_user = User.get_by_email(email)

        if existing_user:
            return False, "Email already exists."
        

        User.add_user(
            name=name,
            email=email,
            password=password
        )

        return True, None


    @staticmethod
    def login(email: str, password: str):

        user = User.get_by_email(email)

        if user is None:
            return False, "Invalid email or password."

        if not user.check_password(password):
            return False, "Invalid email or password."

        login_user(user)

        return True, None