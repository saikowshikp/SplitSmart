from app.models.group import Group
from app.models.notification import Notification
from app.models.user import User

class NotificationType:
    EXPENSE_ADDED="expense_added"
    EXPENSE_EDITED="expense_edited"
    EXPENSE_DELETED="expense_deleted"

    SETTLEMENT_ADDED="settlement_added"

    GROUP_JOINED="group_joined"

class NotificationService:

    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def notify_group(group_id, excluded_users, actor_id, type, message, entity_type, entity_id):
        group=Group.get_group_by_id(group_id)
        users = [gm.user.id for gm in group.members if gm.user.id not in excluded_users]
        actor = User.get_user_by_id(actor_id)
        for user in users:
            Notification.add_notification(
                user_id=user,
                actor_id=actor_id,
                type=type,
                message=f"{actor.name}: "+message,
                entity_type=entity_type,
                entity_id=entity_id
            )

    @staticmethod
    def get_url(type, entity_id):
        if type == NotificationType.EXPENSE_ADDED or type == NotificationType.EXPENSE_EDITED:
            return f"/viewexpense/{entity_id}"
        elif type == NotificationType.EXPENSE_DELETED:
            return f"/group/{entity_id}"

        return "/"

    @staticmethod
    def get_notifications(user_id):
        notifs = Notification.query.filter_by(user_id=user_id)
        notifs_dict = []
        for notif in notifs:
            notification={}
            notification["id"]=notif.id
            notification["message"]=notif.message
            notification["is_read"]=notif.is_read
            notification["created_at"]=notif.created_at
            notification["url"]=NotificationService.get_url(type=notif.type, entity_id=notif.entity_id)
            notifs_dict.append(notification)
        return notifs_dict

    @staticmethod
    def mark_all_read(user_id):
        Notification.mark_all_read(Notification.query.filter_by(user_id=user_id, is_read=False))

    @staticmethod
    def delete_all(user_id):
        Notification.delete_all(Notification.query.filter_by(user_id=user_id))

    @staticmethod
    def delete(notif_id):
        Notification.delete(Notification.query.filter_by(id=notif_id))