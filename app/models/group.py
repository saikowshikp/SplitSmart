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

    @staticmethod
    def get_group_by_id(group_id: int):
        return db.session.query(Group).filter_by(id = group_id).first()

    @staticmethod
    def create_group(group_name, created_by):
        newgroup = Group(name = group_name, created_by = created_by)
        db.session.add(newgroup)
        db.session.commit()
        return newgroup.id
        