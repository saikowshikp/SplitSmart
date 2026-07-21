from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import SubmitField
from wtforms import IntegerField

from wtforms.validators import DataRequired
from wtforms.validators import Length

class CreateGroupForm(FlaskForm):

    group_name = StringField(
        "Group Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50)
        ]
    )

    submit = SubmitField("Create Group")


class JoinGroupForm(FlaskForm):

    group_id = IntegerField(
        "Group ID",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Join Group")