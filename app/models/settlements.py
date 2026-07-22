from datetime import datetime

from app.extensions import db


class Settlement(db.Model):
    __tablename__ = "settlements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.id",
                      ondelete="CASCADE"),
        nullable=False
    )

    payer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    settled_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    notes = db.Column(
        db.String(255)
    )

    group = db.relationship(
        "Group",
        back_populates="settlements"
    )

    payer = db.relationship(
        "User",
        foreign_keys=[payer_id],
        back_populates="payments_made"
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="payments_received"
    )

    @classmethod
    def addsettlement(cls, group_id, payer_id, receiver_id, amount):
        settlement = Settlement(
            group_id=group_id,
            payer_id=payer_id,
            receiver_id=receiver_id,
            amount=amount
        )
        db.session.add(settlement)
        db.session.commit()
        return settlement.id