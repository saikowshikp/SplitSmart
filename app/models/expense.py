from datetime import datetime

from app.extensions import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.id"),
        nullable=False
    )

    paid_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    group = db.relationship(
        "Group",
        back_populates="expenses"
    )

    payer = db.relationship(
        "User",
        back_populates="paid_expenses"
    )

    shares = db.relationship(
        "ExpenseShare",
        back_populates="expense",
        cascade="all, delete-orphan"
    )

    @staticmethod
    def get_expense_by_id(expense_id):
        return db.session.query(Expense).filter_by(id = expense_id).first()

    @staticmethod
    def add_expense_without_commit(group_id, paid_by, title, description, total_amount):
        newExpense = Expense(
            group_id=group_id,
            paid_by=paid_by,
            title=title,
            description=description,
            total_amount=total_amount
        )
        db.session.add(newExpense)
        db.session.flush()
        return newExpense.id