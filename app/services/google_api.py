from datetime import datetime
from math import ceil, log
from string import ascii_uppercase
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


def spacial_range(
    number_of_columns,
    number_of_rows,
    horizontal_offset=0,
    vertical_offset=0,
):
    def int_to_literal_number(number):
        result = []
        base = len(ascii_uppercase)
        for _ in range(ceil(log(number, base))):
            result.append(ascii_uppercase[number % base])
            number //= base
        return ''.join(result[::-1])

    return (f'{int_to_literal_number(horizontal_offset + 1)}'
            f'{vertical_offset + 1}'
            f':{int_to_literal_number(horizontal_offset + number_of_columns)}'
            f'{vertical_offset + number_of_rows}')


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=get_body())
    )
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        )
    )


async def spreadsheets_update_value(
        spreadsheetid: str,
        projects: List[Tuple[str, str, str]],
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    headers = list(SHEET_HEADERS)
    headers[0].append(datetime.now().strftime(FORMAT))
    projects = [[
        project[0],
        f'{project[1]:.2f} days',
        project[2]
    ] for project in projects]
    table_values = [*headers, *projects]
    number_of_rows = len(table_values)
    if number_of_rows > settings.sheet_rows:
        raise ValueError('Слишком много данныых.')
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=spacial_range(
                number_of_columns=settings.sheet_columns,
                number_of_rows=number_of_rows
            ),
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
