from copy import deepcopy
from datetime import datetime
from typing import List, Optional, Tuple

from aiogoogle import Aiogoogle
from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"

SHEET_HEADERS = (
    ['Отчет от'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
)


def get_body(title: Optional[str] = None) -> dict:
    title = title if title else f'Отчет на {datetime.now().strftime(FORMAT)}'
    return dict(
        properties=dict(title=title, locale='ru_RU'),
        sheets=[dict(properties=dict(
            sheetType='GRID',
            sheetId=0,
            title='Лист1',
            gridProperties=dict(
                rowCount=settings.sheet_rows,
                columnCount=settings.sheet_columns
            )
        ))]
    )


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=get_body())
    )
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        )
    )


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: List[Tuple[str, str, str]],
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    headers = deepcopy(SHEET_HEADERS)
    headers[0].append(datetime.now().strftime(FORMAT))
    projects = [[
        project[0],
        f'{project[1]:.2f} days',
        project[2]
    ] for project in projects]
    table_values = [*headers, *projects]
    number_of_rows = len(table_values)
    number_of_columns = max([len(row) for row in table_values])
    if (
        number_of_rows > settings.sheet_rows or
        number_of_columns > settings.sheet_columns
    ):
        raise ValueError(
            f'Слишком много данных. Размер массива для записи'
            f'{number_of_rows}x{number_of_columns}'
            f'превышает выделенное пространство'
            f'{settings.sheet_rows}x{settings.sheet_columns}.'
        )
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=(f'R1C1:R{number_of_rows}'
                   f'C{number_of_columns}'),
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
