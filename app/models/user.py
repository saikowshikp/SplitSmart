from flask_login import UserMixin

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.extensions import login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    group_memberships = db.relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    created_groups = db.relationship(
        "Group",
        back_populates="creator",
    )

    paid_expenses = db.relationship(
        "Expense",
        back_populates="payer",
    )

    expense_shares = db.relationship(
        "ExpenseShare",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    payments_made = db.relationship(
        "Settlement",
        foreign_keys="Settlement.payer_id",
        back_populates="payer",
    )

    payments_received = db.relationship(
        "Settlement",
        foreign_keys="Settlement.receiver_id",
        back_populates="receiver",
    )

    def set_password(self, password: str) -> None:
        """Hash and store a user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(
            self.password_hash,
            password,
        )

    @classmethod
    def get_by_email(cls, email: str):
        """Return the user with the given email, if one exists."""
        return cls.query.filter_by(
            email=email.strip().lower()
        ).first()

    @classmethod
    def get_user_by_id(cls, user_id: int):
        """Return the user with the given ID, if one exists."""
        return db.session.get(cls, user_id)

    @classmethod
    def exists(cls, user_id: int) -> bool:
        """Return whether a user with the given ID exists."""
        return db.session.get(cls, user_id) is not None

    def to_dict(self) -> dict:
        """Return safe public user data."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }


@login_manager.user_loader
def load_user(user_id: str):
    """Load a user from the Flask-Login session."""
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return db.session.get(User, user_id)
