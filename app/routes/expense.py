from flask import Blueprint, render_template, request, url_for, redirect, flash, session

from flask_login import login_required
from flask_login import current_user

from app.models.group import Group
from app.models.expense import Expense

from app.services.expense_service import ExpenseService
from app.services.settlement_service import SettlementService
from app.services.notification_service import NotificationService, NotificationType


expense_bp = Blueprint("expense", __name__)


@expense_bp.get("/viewexpense/<int:expense_id>")
@login_required
def view_expense(expense_id: int):
    """Display an expense if the current user has access to it."""

    expense = ExpenseService.get_accessible_expense(
        expense_id=expense_id,
        user_id=current_user.id,
    )

    if expense is None:
        flash("Expense not found.", "info")
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "viewexpense.html",
        expense=expense,
        shares=expense.shares,
    )



@expense_bp.route(
    "/addexpense/<int:groupid>",
    methods=["GET","POST"]
)
@login_required
def addexpense(groupid):
    draft = session.pop('expense_draft', None)
    group = Group.get_group_by_id(groupid)

    if group is None or \
        not Group.is_user_member(current_user.id, group):

        flash("Group Not Found", "info")
        return redirect(url_for("dashboard.dashboard"))


    if request.method == "POST":

        shares = []

        for member_id in request.form.getlist("members"):

            shares.append(
                (
                    int(member_id),
                    float(
                        request.form[f"share_{member_id}"]
                    )
                )
            )


        success, message, expense = ExpenseService.create_expense(
            group_id=groupid,
            payer_id=int(request.form["payer"]),
            title=request.form["title"],
            description=request.form["description"],
            amount=float(request.form["amount"]),
            shares=shares
        )


        if not success:
            flash(message,"danger")
            return redirect(request.url)

        NotificationService.notify_group(
            group_id=groupid,
            excluded_users=[current_user.id],
            actor_id=current_user.id,
            type=NotificationType.EXPENSE_ADDED,
            message=f"Added expense \"{expense.title}\"",
            entity_type="expense",
            entity_id=expense.id,
        )

        flash(
            "Expense added successfully",
            "success"
        )


        return redirect(
            url_for(
                "group.group",
                groupid=groupid
            )
        )


    return render_template(
        "addexpense.html",
        group=group,
        members=[
            m.user
            for m in group.members
        ],
        draft = draft
    )


@expense_bp.route("/editexpense/<int:expenseid>", methods=["GET", "POST"])
@login_required
def editexpense(expenseid):

    expense = Expense.get_expense_by_id(expenseid)
    group = expense.group

    if expense is None or \
        current_user.id not in [gm.user.id for gm in group.members]:
        
        flash("Expense not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    if not ExpenseService.user_has_access(
        current_user.id,
        expense
    ):
        flash("You are not authorized to edit this expense.", "danger")
        return redirect(
            url_for(
                "group.group",
                groupid=expense.group_id
            )
        )

    members = [member.user for member in expense.group.members]

    if request.method == "POST":

        shares = []

        for member_id in request.form.getlist("members"):

            shares.append(
                (
                    int(member_id),
                    float(
                        request.form[f"share_{member_id}"]
                    )
                )
            )

        success, message = ExpenseService.update_expense(
            expense=expense,
            title=request.form["title"],
            description=request.form["description"],
            payer_id=int(request.form["payer"]),
            amount=float(request.form["amount"]),
            shares=shares
        )

        if not success:

            flash(message, "danger")

            return render_template(
                "editexpense.html",
                expense=expense,
                members=members
            )

        flash(
            "Expense updated successfully.",
            "success"
        )

        NotificationService.notify_group(
            group_id=expense.group_id,
            excluded_users=[current_user.id],
            actor_id=current_user.id,
            type=NotificationType.EXPENSE_EDITED,
            message=f"Edited expense \"{expense.title}\"",
            entity_type="expense",
            entity_id=expense.id,
        )

        return redirect(
            url_for(
                "group.group",
                groupid=expense.group_id
            )
        )

    return render_template(
        "editexpense.html",
        expense=expense,
        members=members
    )


@expense_bp.route(
    "/deleteexpense/<int:expenseid>"
)
@login_required
def deleteexpense(expenseid):

    expense = Expense.get_expense_by_id(
        expenseid
    )


    if not ExpenseService.user_has_access(
        current_user.id,
        expense
    ):
        flash("You are not authorized to delete the expense.", "danger")
        return redirect(url_for("dashboard.dashboard"))


    ExpenseService.delete_expense(
        expense
    )

    NotificationService.notify_group(
        group_id=expense.group_id,
        excluded_users=[current_user.id],
        actor_id=current_user.id,
        type=NotificationType.EXPENSE_DELETED,
        message=f"Deleted expense \"{expense.title}\"",
        entity_type="group",
        entity_id=expense.group_id,
    )


    flash(
        "Expense deleted",
        "success"
    )


    return redirect(
        url_for(
            "group.group",
            groupid=expense.group_id
        )
    )



@expense_bp.route(
    "/checkbalances/<int:groupid>"
)
@login_required
def checkbalances(groupid):

    group = Group.get_group_by_id(
        groupid
    )


    if current_user.id not in [
        member.user.id
        for member in group.members
    ]:
        flash("You are not authorized to see this page.", "danger")
        return redirect(url_for("dashboard.dashboard"))


    balances = ExpenseService.calculate_balances(
        group
    )

    simplified_payments = SettlementService.simplify_payments(balances)

    return render_template(
        "balances.html",
        group=group,
        balances=balances,
        simplified_payments=simplified_payments
    )