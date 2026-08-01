from flask import Blueprint, jsonify

from flask_login import login_required, current_user

from app.services.notification_service import NotificationService

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/count")
@login_required
def notification_count():

    count = NotificationService.get_unread_count(
        user_id=current_user.id
    )

    return jsonify({
        "count": count
    })


@notification_bp.route("/notifications")
@login_required
def notifications():

    notifs = NotificationService.get_notifications(
        user_id=current_user.id
    )
    return jsonify(notifs)


@notification_bp.route("/notifications/mark_read", methods=["POST"])
@login_required
def mark_read():

    NotificationService.mark_all_read(
        user_id=current_user.id
    )

    return "", 204


@notification_bp.route("/notifications/delete_all", methods=["POST"])
@login_required
def delete_all():

    NotificationService.delete_all(
        user_id=current_user.id
    )

    return "", 204


@notification_bp.route("/notifications/delete/<int:notif_id>", methods=["POST"])
@login_required
def delete(notif_id):

    NotificationService.delete(
        notif_id=notif_id
    )

    return "", 204