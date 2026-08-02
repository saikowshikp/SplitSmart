from typing import Optional, Tuple

from flask_login import login_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User


class AuthService:
    """Business logic related to user authentication."""

    INVALID_CREDENTIALS = "Invalid email or password."
    REGISTRATION_ERROR = "Unable to create account."

    @staticmethod
    def register(
        name: str,
        email: str,
        password: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Create a new user account.

        Returns:
            (True, None) on success.
            (False, error_message) on failure.
        """

        name = name.strip()
        email = email.strip().lower()

        # This provides a fast and user-friendly check.
        # The database UNIQUE constraint is still required
        # to handle concurrent requests safely.
        if User.get_by_email(email):
            return False, "Email already exists."


        user = User(
            name=name,
            email=email,
        )


        user.set_password(password)


        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            # This can happen if another request created
            # the same email between our check and INSERT.
            return False, "Email already exists."

        except Exception:
            db.session.rollback()

            # Do not expose internal database errors to users.
            return False, AuthService.REGISTRATION_ERROR

        return True, None

    @staticmethod
    def login(
        email: str,
        password: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Authenticate a user and create their login session.

        Returns:
            (True, None) on successful authentication.
            (False, error_message) otherwise.
        """

        email = email.strip().lower()

        user = User.get_by_email(email)

        if user is None:
            return False, AuthService.INVALID_CREDENTIALS

        if not user.check_password(password):
            return False, AuthService.INVALID_CREDENTIALS

        login_user(user)

        return True, None
    