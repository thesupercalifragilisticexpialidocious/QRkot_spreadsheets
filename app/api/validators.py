from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import project_crud
from app.models import CharityProject
from app.schemas.charity_project import ProjectUpdate


async def check_name_duplicates(name: str, session: AsyncSession) -> None:
    project_id = await project_crud.get_by_name(name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_exists(
        id: int,
        session: AsyncSession,
) -> CharityProject:
    project: CharityProject = await project_crud.get(id, session)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return project


def check_project_open(project: CharityProject) -> None:
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )


def ensure_no_nullification_during_update(obj_in: ProjectUpdate) -> None:
    for field in obj_in.dict(exclude_unset=True).values():
        if not field:
            raise HTTPException(
                status_code=422,
                detail=('Нельзя занулять поля.')
            )


def ensure_new_goal_is_above_current_ballance(
    obj_in: ProjectUpdate, project: CharityProject
) -> None:
    if obj_in.full_amount < project.invested_amount:
        raise HTTPException(
            status_code=422,
            detail=(f'Цель не может быть ниже текущих инвестиций'
                    f'{project.invested_amount}')
        )


def check_ballance_before_removal(project: CharityProject) -> None:
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
