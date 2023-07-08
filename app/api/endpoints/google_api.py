from datetime import timedelta
from typing import List, Tuple

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)
from app.models import CharityProject

router = APIRouter()


@router.post(
    '/',
    response_model=List[List[str]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    projects = await project_crud.get_projects_by_completion_rate(session)
    projects = [[
        project[0],
        f'{project[1]:.2f} days',
        project[2]
    ] for project in projects]
    spreadsheetid = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheetid, wrapper_services)
    await spreadsheets_update_value(spreadsheetid, projects, wrapper_services)
    return projects
