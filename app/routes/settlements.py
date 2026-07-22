from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from app.models.group import Group
from app.services.settlement_service import SettlementService


settlement_bp = Blueprint("settlement", __name__)


@settlement_bp.route("/settle/<int:groupid>", methods=["GET", "POST"])
@login_required
def settle(groupid):

    group = Group.get_group_by_id(groupid)

    if group is None:

        flash("Invalid Group.", "danger")

        return redirect(
            url_for("dashboard.dashboard")
        )


    if not SettlementService.user_has_access(current_user.id, groupid):

        flash(
            "You cannot access this group.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )


    members = [
        gm.user
        for gm in group.members
    ]


    if request.method == "POST":

        payer_id = int(
            request.form["payer_id"]
        )

        receiver_id = int(
            request.form["receiver_id"]
        )

        amount = float(
            request.form["amount"]
        )

        success, message = SettlementService.settle(
            group_id=groupid,
            payer_id=payer_id,
            receiver_id=receiver_id,
            amount=amount
        )

        if not success:
            flash(message, "danger")
            return redirect(request.url)
        

        flash(
            "Settlement recorded successfully.",
            "success"
        )

        return redirect(
            url_for(
                "group.group",
                groupid=groupid
            )
        )


    payer_id = request.args.get(
        "payer_id",
        type=int
    )

    receiver_id = request.args.get(
        "receiver_id",
        type=int
    )

    amount = request.args.get(
        "amount",
        type=float
    )


    return render_template(
        "addsettlement.html",
        group=group,
        members=members,
        payer_id=payer_id,
        receiver_id=receiver_id,
        amount=amount
    )