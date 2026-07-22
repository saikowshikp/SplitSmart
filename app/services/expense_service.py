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
        
        for _, share_amount in shares:
            if share_amount < 0:
                return False, "Share amount cannot be negative"


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
        
        for _, share_amount in shares:
            if share_amount < 0:
                return False, "Share amount cannot be negative"
        

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
        
        balance_map = {
            member.user.id: {
                "user_id": member.user.id,
                "user_name": member.user.name,
                "amount": 0.0
            }
            for member in group.members
        }

       
        for expense in group.expenses:
            balance_map[expense.payer.id]["amount"] += float(expense.total_amount)

            for share in expense.shares:
                balance_map[share.user_id]["amount"] -= float(share.amount_owed)

        for settlement in group.settlements:
            balance_map[settlement.payer_id]["amount"] += float(settlement.amount)
            balance_map[settlement.receiver_id]["amount"] -= float(settlement.amount)

        
        balances = list(balance_map.values())

        # Optional: round amounts to 2 decimals and avoid -0.0
        for item in balances:
            item["amount"] = round(item["amount"], 2)
            if abs(item["amount"]) < 0.005:
                item["amount"] = 0.0

        
        balances.sort(key=lambda x: x["amount"], reverse=True)

        return balances