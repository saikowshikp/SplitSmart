from flask import Blueprint, render_template, request, url_for, redirect

from flask_login import login_required
from flask_login import current_user

from app.models.group import Group
from app.models.group_members import GroupMember

group_bp = Blueprint("group", __name__)

@group_bp.route("/group/<int:groupid>")
@login_required
def group(groupid):
    if(not GroupMember.is_member(groupid, current_user.id)):
        return "You are not a member of this group"
    
    current_group = Group.get_group_by_id(groupid)
    return render_template("group.html",
                           group = current_group,
                           user = current_user)

@group_bp.route("/creategroup", methods=["GET", "POST"])
@login_required
def creategroup():
    if request.method == "POST":
        group_name = request.form["groupname"]
        group_id = Group.create_group(group_name, current_user.id)
        GroupMember.add_group_member(group_id, current_user.id)
        return redirect(url_for("dashboard.dashboard"))
    
    return render_template(
        "creategroup.html",
        user=current_user
    )

@group_bp.route("/joingroup", methods=["GET", "POST"])
@login_required
def joingroup():
    if request.method == "POST":
        group_id = (int)(request.form["group_id"])

        if group_id in [grpmem.group_id for grpmem in current_user.group_memberships]:
            return "You are already in the group"
        
        if Group.get_group_by_id(group_id) is not None:
            GroupMember.add_group_member(group_id, current_user.id)
            return redirect(url_for("group.group", groupid=group_id))
        
        return "Invalid Group id"
    
    return render_template("joingroup.html", user=current_user)