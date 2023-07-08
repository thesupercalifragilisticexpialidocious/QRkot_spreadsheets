from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        # = await await session.get(self.model, pk)
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def get_all_open(
        self,
        session: AsyncSession
    ):
        '''Get Transaction instances, whose 'fully invested' flag is FALSE.'''
        db_objs = await session.execute(
            select(self.model).where(self.model.fully_invested == False)  # noqa
        )
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: Optional[AsyncSession] = None,
        user: Optional[User] = None,
        commit: bool = True
    ):
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        db_obj.invested_amount = 0
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_by_attribute(
            self,
            attr_name: str,
            attr_value: str,
            session: AsyncSession,
    ):
        attr = getattr(self.model, attr_name)
        db_obj = await session.execute(
            select(self.model).where(attr == attr_value)
        )
        return db_obj.scalars().first()
