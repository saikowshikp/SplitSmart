from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class RegisterForm(FlaskForm):

    name = StringField(
        "Name",
        filters=[lambda value: value.strip() if value else value],
        validators=[
            DataRequired(message="Name is required."),
            Length(
                min=2,
                max=50,
                message="Name must be between 2 and 50 characters.",
            ),
        ],
    )

    email = StringField(
        "Email",
        filters=[
            lambda value: value.strip().lower() if value else value
        ],
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(
                max=120,
                message="Email address is too long.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(
                min=8,
                max=128,
                message="Password must be between 8 and 128 characters.",
            ),
        ],
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        filters=[
            lambda value: value.strip().lower() if value else value
        ],
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(
                max=120,
                message="Email address is too long.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(
                min=8,
                max=128,
                message="Password must be between 8 and 128 characters.",
            ),
        ],
    )

    submit = SubmitField("Login")
