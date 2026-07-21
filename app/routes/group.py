from flask import Blueprint, render_template, url_for, redirect, flash

from flask_login import login_required
from flask_login import current_user

from app.models.group import Group
from app.models.group_members import GroupMember

from app.forms.group_forms import JoinGroupForm, CreateGroupForm
from app.services.group_service import GroupService

group_bp = Blueprint("group", __name__)

@group_bp.route("/group/<int:groupid>")
@login_required
def group(groupid):

    if not GroupMember.is_member(
        groupid,
        current_user.id
    ):
        flash(
            "You are not a member of this group.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    group = Group.get_group_by_id(groupid)

    return render_template(
        "group.html",
        group=group
    )



@group_bp.route(
    "/creategroup",
    methods=["GET", "POST"]
)
@login_required
def creategroup():

    form = CreateGroupForm()

    if form.validate_on_submit():

        success, result = GroupService.create_group(
            form.group_name.data,
            current_user.id
        )

        if not success:

            flash(result, "danger")

            return render_template(
                "creategroup.html",
                form=form
            )

        flash(
            "Group created successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "creategroup.html",
        form=form
    )



@group_bp.route(
    "/joingroup",
    methods=["GET", "POST"]
)
@login_required
def joingroup():

    form = JoinGroupForm()

    if form.validate_on_submit():

        success, result = GroupService.join_group(
            form.group_id.data,
            current_user
        )

        if not success:

            flash(result, "danger")

            return render_template(
                "joingroup.html",
                form=form
            )

        flash(
            "Joined group successfully.",
            "success"
        )

        return redirect(
            url_for(
                "group.group",
                groupid=result.id
            )
        )

    return render_template(
        "joingroup.html",
        form=form
    )