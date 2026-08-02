from app.extensions import db

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    creator = db.relationship(
        "User",
        back_populates = "created_groups"
    )

    members = db.relationship(
        "GroupMember",
        back_populates = "group",
        cascade = "all, delete-orphan"
    )

    expenses = db.relationship(
        "Expense",
        back_populates="group",
        cascade="all, delete-orphan"
    )

    settlements = db.relationship(
        "Settlement",
        back_populates="group",
        cascade="all, delete-orphan"
    )

    @staticmethod
    def is_user_member(user_id, group):
        return user_id in [gm.user.id for gm in group.members]

    @classmethod
    def get_group_by_id(cls, group_id: int):
        return db.session.get(cls, group_id)

    @staticmethod
    def create_group(group_name, created_by):
        newgroup = Group(name = group_name, created_by = created_by)
        db.session.add(newgroup)
        db.session.commit()
        return newgroup.id
        