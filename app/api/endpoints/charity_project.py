from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_ballance_before_removal, check_name_duplicates,
    check_project_exists, check_project_open,
    ensure_new_goal_is_above_current_ballance,
    ensure_no_nullification_during_update
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject
from app.schemas.charity_project import (
    ProjectCreate, ProjectDB, ProjectUpdate
)
from app.services.accounting import distribute

router = APIRouter()


@router.get(
    '/',
    response_model=List[ProjectDB],
    response_model_exclude_none=True
)
async def get_all_projects(session: AsyncSession = Depends(get_async_session)):
    projects = await project_crud.get_multi(session)
    return projects


@router.post(
    '/',
    response_model=ProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_project(
    project: ProjectCreate,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    await check_name_duplicates(project.name, session)
    project = await project_crud.create(project, session, commit=False)
    session.add_all(distribute(
        target=project,
        sources=await donation_crud.get_all_open(session)
    ))
    await session.commit()
    await session.refresh(project)
    return project


@router.patch(
    '/{project_id}',
    response_model=ProjectDB,
    # response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_project(
    project_id: int,
    obj_in: ProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    project: CharityProject = await check_project_exists(project_id, session)
    check_project_open(project)
    ensure_no_nullification_during_update(obj_in)
    if obj_in.name is not None:
        await check_name_duplicates(obj_in.name, session)
    if obj_in.full_amount is not None:
        ensure_new_goal_is_above_current_ballance(obj_in, project)
    project = await project_crud.update(project, obj_in, session)
    return project


@router.delete(
    '/{project_id}',
    response_model=ProjectDB,
    # response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def remove_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    project: CharityProject = await check_project_exists(project_id, session)
    check_ballance_before_removal(project)
    check_project_open(project)
    project = await project_crud.remove(project, session)
    return project
