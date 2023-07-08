from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, NonNegativeInt, PositiveInt


class ProjectBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str]
    full_amount: Optional[PositiveInt]

    class Config:
        min_anystr_length = 1
        extra = Extra.forbid


class ProjectCreate(ProjectBase):
    name: str = Field(..., max_length=100)
    description: str
    full_amount: PositiveInt


class ProjectDB(ProjectCreate):
    id: int
    invested_amount: NonNegativeInt
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class ProjectUpdate(ProjectBase):
    pass
