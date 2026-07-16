from flask import Blueprint, render_template, request, url_for, redirect

from flask_login import login_required
from flask_login import current_user

from app.models.group import Group
from app.models.expense import Expense
from app.models.expense_share import ExpenseShare

expense_bp = Blueprint("expense", __name__)

@expense_bp.route("/viewexpense/<int:expense_id>")
@login_required
def viewexpense(expense_id):
    expense = Expense.get_expense_by_id(expense_id = expense_id)
    if current_user.id in [grp_member.user.id for grp_member in expense.group.members]:
        return render_template("viewexpense.html",
                               user = current_user,
                               expense = expense,
                               shares = expense.shares)
    else:
        return "You cannot view this expense"

@expense_bp.route("/addexpense/<int:groupid>", methods=["GET", "POST"])
@login_required
def addexpense(groupid):

    current_group = Group.get_group_by_id(groupid)

    if current_group is None:
        return "Invalid group"

    members = [gm.user for gm in current_group.members]

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        payer_id = int(request.form["payer"])
        amount = float(request.form["amount"])
        selected_members = request.form.getlist("members")

        if len(selected_members) == 0:
            return "Select at least one member."

        total_share = 0

        shares = []

        for member_id in selected_members:
            share = float(request.form[f"share_{member_id}"])
            total_share += share
            shares.append(
                (
                    int(member_id),
                    share
                )
            )

        if abs(total_share - amount) > 0.01:
            return "Sum of shares must equal total amount."

        expense_id = Expense.add_expense_without_commit(
            group_id=groupid,
            paid_by=payer_id,
            title=title,
            description=description,
            total_amount=amount
        )

        ExpenseShare.add_expenseshares(shares=shares, expense_id=expense_id)

        return redirect(
            url_for(
                "group.group",
                groupid=groupid
            )
        )

    return render_template(
        "addexpense.html",
        user=current_user,
        group=current_group,
        members=members
    )

@expense_bp.route("/checkbalances/<int:groupid>")
@login_required
def checkbalances(groupid):
    group = Group.get_group_by_id(group_id=groupid)


    if current_user.id in [member.user.id for member in group.members]:
        balances = {}
        for member in group.members:
            balances[member.user.id] = 0.0

        for expense in group.expenses:
            balances[expense.payer.id] = balances[expense.payer.id] + expense.total_amount

            for share in expense.shares:
                balances[share.user_id] = balances[share.user.id] - share.amount_owed
        
        return render_template("balances.html",
                           user = current_user,
                           group = group,
                           balances = balances)
    else:
        return "You are not part of this group"