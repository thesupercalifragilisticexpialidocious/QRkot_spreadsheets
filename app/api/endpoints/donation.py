from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.accounting import distribute
from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app. crud.charity_project import project_crud
from app.crud.donation import donation_crud
from app.models import Donation, User
from app.schemas.donation import AdminDonationDB, DonationCreate, MyDonationDB

router = APIRouter()


@router.post(
    '/',
    response_model=MyDonationDB,
    response_model_exclude_none=True
)
async def donate(
        donat: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> Donation:
    donat = await donation_crud.create(donat, session, user, commit=False)
    session.add_all(distribute(
        target=donat,
        sources=await project_crud.get_all_open(session)
    ))
    await session.commit()
    await session.refresh(donat)
    return donat


@router.get(
    '/',
    response_model=List[AdminDonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def get_donations(session: AsyncSession = Depends(get_async_session)):
    donations = await donation_crud.get_multi(session)
    return donations


@router.get('/my', response_model=list[MyDonationDB])
async def get_my_reservations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
) -> List[Donation]:
    donations = await donation_crud.get_by_user(session, user)
    return donations
