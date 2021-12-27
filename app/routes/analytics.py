from typing import List

from fastapi import APIRouter

from app.models.analytics import Aggregate, Stats, Timeseries, TimeseriesPeriod
from app.services.analytics import Pipeline, post_stats

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("")
async def analytics_stats(stats: Stats):
    return await post_stats(stats.dict())


@router.get("/aggregate", response_model=Aggregate)
async def aggregate(period: TimeseriesPeriod = TimeseriesPeriod.last_7_days):
    return await Pipeline(period.value).get_aggregate()


@router.get("/timeseries", response_model=List[Timeseries])
async def timeseries(period: TimeseriesPeriod = TimeseriesPeriod.last_7_days):
    return await Pipeline(period.value).get_timeseries()


@router.get("/breakdown", response_model=None)
async def breakdown(period: TimeseriesPeriod = TimeseriesPeriod.last_7_days):
    pass
