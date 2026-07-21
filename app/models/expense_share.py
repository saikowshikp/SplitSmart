from app.extensions import db


class ExpenseShare(db.Model):
    __tablename__ = "expense_shares"

    expense_id = db.Column(
        db.Integer,
        db.ForeignKey("expenses.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    amount_owed = db.Column(
        db.Float,
        nullable=False
    )

    expense = db.relationship(
        "Expense",
        back_populates="shares"
    )

    user = db.relationship(
        "User",
        back_populates="expense_shares"
    )

    def add_expenseshares(shares, expense_id):
        for member_id, share in shares:

            expense_share = ExpenseShare(
                expense_id=expense_id,
                user_id=member_id,
                amount_owed=share
            )

            db.session.add(expense_share)

        db.session.commit()