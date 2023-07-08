from sqlalchemy import Column, ForeignKey, Integer, Text

from .base import Transaction


class Donation(Transaction):
    user_id = Column(Integer, ForeignKey(
        'user.id',
        name='fk_donation_user_id_user'
    ))
    comment = Column(Text)

    def __repr__(self) -> str:
        return f'@{self.user_id} {super().__repr__()}'
