from app.extensions import db

class GroupMember(db.Model):
    __tablename__ = "group_members"

    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key = True)

    group = db.relationship("Group", back_populates="members")
    user = db.relationship("User", back_populates = "group_memberships")
    
    @staticmethod
    def add_group_member(group_id, user_id):
        group_member = GroupMember(group_id = group_id, user_id = user_id)
        db.session.add(group_member)
        db.session.commit()

    @staticmethod
    def is_member(group_id, user_id):
        return db.session.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first() is not None