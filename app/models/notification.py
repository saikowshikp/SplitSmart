from app.extensions import db

from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    type = db.Column(
        db.String(50),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    entity_type = db.Column(
        db.String(50),
        nullable=False
    )

    entity_id = db.Column(
        db.Integer,
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    @staticmethod
    def add_notification(user_id, actor_id, type, message, entity_type, entity_id):
        new_notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            type=type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        db.session.add(new_notification)
        db.session.commit()
        return new_notification.id

    @staticmethod
    def mark_all_read(notifications):
        notifications.update({"is_read":True})
        db.session.commit()

    @staticmethod
    def delete_all(notifications):
        notifications.delete()
        db.session.commit()

    @staticmethod
    def delete(notification):
        notification.delete()
        db.session.commit()