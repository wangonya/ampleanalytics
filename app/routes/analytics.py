from typing import List

from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User

from app.models.analytics import (
    Aggregate,
    Breakdown,
    Stats,
    Timeseries,
    TimeseriesPeriod,
)
from app.services.analytics import Pipeline, post_stats
from app.services.auth import auth

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("")
async def analytics_stats(stats: Stats):
    return await post_stats(stats.dict())


@router.get(
    "/aggregate",
    response_model=Aggregate,
    dependencies=[Depends(auth.implicit_scheme)],
)
async def aggregate(
    period: TimeseriesPeriod = TimeseriesPeriod.last_7_days,
    user: Auth0User = Security(auth.get_user),
):
    return await Pipeline(period.value).get_aggregate()


@router.get("/timeseries", response_model=List[Timeseries])
async def timeseries(period: TimeseriesPeriod = TimeseriesPeriod.last_7_days):
    return await Pipeline(period.value).get_timeseries()


@router.get("/breakdown", response_model=Breakdown)
async def breakdown(period: TimeseriesPeriod = TimeseriesPeriod.last_7_days):
    return await Pipeline(period.value).get_breakdown()
