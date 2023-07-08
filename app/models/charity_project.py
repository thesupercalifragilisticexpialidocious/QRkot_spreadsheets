from sqlalchemy import Column, String, Text

from .base import Transaction


class CharityProject(Transaction):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'#{self.name} {super().__repr__()}'
