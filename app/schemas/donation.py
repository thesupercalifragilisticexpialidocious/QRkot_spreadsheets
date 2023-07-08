from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, NonNegativeInt, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    pass


class MyDonationDB(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class AdminDonationDB(MyDonationDB):
    user_id: int
    invested_amount: NonNegativeInt
    fully_invested: bool
    close_date: Optional[datetime]
