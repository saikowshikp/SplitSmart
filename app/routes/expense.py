from flask import Blueprint, render_template, request, url_for, redirect, flash

from flask_login import login_required
from flask_login import current_user

from app.models.group import Group
from app.models.expense import Expense

from app.services.expense_service import ExpenseService
from app.services.settlement_service import SettlementService

expense_bp = Blueprint("expense", __name__)

@expense_bp.route("/viewexpense/<int:expense_id>")
@login_required
def viewexpense(expense_id):

    expense = Expense.get_expense_by_id(expense_id)


    if not ExpenseService.user_has_access(
        current_user.id,
        expense
    ):
        flash("Cannot access expense", "info")
        return redirect(url_for("dashboard.dashboard"))


    return render_template(
        "viewexpense.html",
        expense=expense,
        shares=expense.shares
    )



@expense_bp.route(
    "/addexpense/<int:groupid>",
    methods=["GET","POST"]
)
@login_required
def addexpense(groupid):

    group = Group.get_group_by_id(groupid)


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


        success, message = ExpenseService.create_expense(
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
        ]
    )


@expense_bp.route("/editexpense/<int:expenseid>", methods=["GET", "POST"])
@login_required
def editexpense(expenseid):

    expense = Expense.get_expense_by_id(expenseid)

    if expense is None:
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