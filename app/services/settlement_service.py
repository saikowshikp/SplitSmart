from app.models.group import Group
from app.models.settlements import Settlement

class SettlementService:
    def user_has_access(user_id, group_id):
        group = Group.get_group_by_id(group_id)
        if user_id in [member.user.id for member in group.members]:
            return True
        
        return False
    
    @classmethod
    def settle(cls, group_id, payer_id, receiver_id, amount):
        if payer_id == receiver_id:
            return False, "Payer and receiver cannot be the same."


        if not cls.user_has_access(payer_id, group_id) or not cls.user_has_access(receiver_id, group_id):

            return False, "Invalid members selected."


        if amount <= 0:

            return False, "Amount should be greater than zero."
        
        Settlement.addsettlement(
            group_id = group_id,
            payer_id = payer_id,
            receiver_id = receiver_id,
            amount = amount
        )

        return True, None
    
    @staticmethod
    def simplify_payments(balances):

        creditors = []
        debtors = []

        for balance in balances:

            if balance["amount"] > 0.01:

                creditors.append(balance.copy())

            elif balance["amount"] < -0.01:

                debtor = balance.copy()
                debtor["amount"] = -debtor["amount"]   # store positive debt

                debtors.append(debtor)

        creditors.sort(key=lambda x:x["amount"], reverse=True)
        debtors.sort(key=lambda x:x["amount"], reverse=True)

        creditor_idx = 0
        debtor_idx = 0

        simplified = []

        while creditor_idx < len(creditors) and debtor_idx < len(debtors):

            creditor = creditors[creditor_idx]
            debtor = debtors[debtor_idx]

            amount = min(
                creditor["amount"],
                debtor["amount"]
            )

            simplified.append({

                "payer_id": debtor["user_id"],
                "payer_name": debtor["user_name"],

                "receiver_id": creditor["user_id"],
                "receiver_name": creditor["user_name"],

                "amount": round(amount, 2)

            })

            creditor["amount"] -= amount
            debtor["amount"] -= amount

            if creditor["amount"] < 0.01:
                creditor_idx += 1

            if debtor["amount"] < 0.01:
                debtor_idx += 1

        return simplified