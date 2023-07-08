from datetime import datetime

from sqlalchemy import Boolean, Column, CheckConstraint, DateTime, Integer

from app.core.db import Base


class Transaction(Base):
    __abstract__ = True
    __table_args__ = (CheckConstraint(
        ('invested_amount >= 0 AND full_amount > 0 AND '
         'full_amount >= invested_amount')
    ),)
    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)

    create_date = Column(DateTime, default=datetime.now)
    # now as callable must be passed for stamps to vary
    close_date = Column(DateTime)

    def remainder(self) -> int:
        return self.full_amount - self.invested_amount

    def complete(self) -> None:
        # self.invested_amount = self.full_amount
        self.fully_invested = True
        self.close_date = datetime.now()

    def __repr__(self) -> str:
        return f'${self.full_amount} ({self.create_date})'
