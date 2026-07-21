from app.models.expense import Expense
from app.models.expense_share import ExpenseShare


class ExpenseService:


    @staticmethod
    def user_has_access(user_id, expense):

        return user_id in [
            member.user.id
            for member in expense.group.members
        ]



    @staticmethod
    def create_expense(
        group_id,
        payer_id,
        title,
        description,
        amount,
        shares
    ):

        if len(shares) == 0:
            return False, "Select at least one member."


        total_share = sum(
            share[1]
            for share in shares
        )


        if abs(total_share - amount) > 0.01:
            return False, "Sum of shares must equal total amount."


        expense_id = Expense.add_expense_without_commit(
            group_id=group_id,
            paid_by=payer_id,
            title=title,
            description=description,
            total_amount=amount
        )


        ExpenseShare.add_expenseshares(
            shares=shares,
            expense_id=expense_id
        )


        return True, expense_id



    @staticmethod
    def update_expense(
        expense,
        title,
        description,
        payer_id,
        amount,
        shares
    ):

        if len(shares) == 0:
            return False, "Select at least one member."

        total_share = sum(
            share_amount
            for _, share_amount in shares
        )

        if abs(total_share - amount) > 0.01:
            return False, "Sum of shares must equal total amount."

        try:

            # Update expense details
            expense.title = title
            expense.description = description
            expense.paid_by = payer_id
            expense.total_amount = amount

            # Remove existing shares
            expense.shares.clear()

            # Add updated shares
            for user_id, amount_owed in shares:

                expense.shares.append(
                    ExpenseShare(
                        user_id=user_id,
                        amount_owed=amount_owed
                    )
                )

            Expense.commit()

            return True, None

        except Exception:

            Expense.rollback()

            return False, "Unable to update expense."



    @staticmethod
    def delete_expense(expense):

        Expense.delete_expense(
            expense.id
        )



    @staticmethod
    def calculate_balances(group):

        balances = {}

        for member in group.members:
            balances[member.user.id] = 0.0


        for expense in group.expenses:

            balances[expense.payer.id] += expense.total_amount


            for share in expense.shares:

                balances[share.user_id] -= share.amount_owed


        return balances