from typing import List, Optional, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDProject(CRUDBase):

    @staticmethod
    async def get_by_name(name: str, session: AsyncSession) -> Optional[int]:
        db_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == name)
        )
        db_id = db_id.scalars().first()
        return db_id

    @staticmethod
    async def get_projects_by_completion_rate(
        session: AsyncSession
    ) -> List[Tuple[str, float, str]]:
        projects = await session.execute(
            select(
                CharityProject.name,
                (func.julianday(
                    CharityProject.close_date
                ) - func.julianday(
                    CharityProject.create_date
                )).label('rate'),
                CharityProject.description
            ).where(
                CharityProject.fully_invested is True
            ).order_by(desc('rate'))
        )
        return projects.all()


project_crud = CRUDProject(CharityProject)
