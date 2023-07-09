from aiogoogle import Aiogoogle, excs
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)

SHEET_URL = 'https://docs.google.com/spreadsheets/d/{}'

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    try:
        file_id = await spreadsheets_create(wrapper_services)
    except excs.AiogoogleError as e:
        raise HTTPException(f'Не получилось создать документ: {e}')
    try:
        await set_user_permissions(file_id, wrapper_services)
    except excs.AiogoogleError as e:
        raise HTTPException(f'Не получилось расшарить документ: {e}')
    projects = await project_crud.get_projects_by_completion_rate(session)
    try:
        await spreadsheets_update_value(file_id, projects, wrapper_services)
    except Exception as e:
        raise HTTPException(f'Не получилось записать данные: {e}')
    return SHEET_URL.format(file_id)
