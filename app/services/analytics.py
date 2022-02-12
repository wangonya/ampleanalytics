from datetime import datetime, timedelta
from typing import List

from app.services import db_client

today = datetime.now().replace(hour=0, minute=0, second=1)
period_unit = {
    "today": (today, "hour"),
    "last_7_days": (today - timedelta(days=6), "day"),
    "last_30_days": (today - timedelta(days=29), "day"),
}


class Pipeline:
    def __init__(self, period) -> None:
        self.start, self.unit = period_unit.get(period)
        self.pipeline = [
            {
                "$match": {
                    "request_time": {"$gte": self.start},
                },
            },
        ]

    async def get_aggregate(self):
        self.pipeline.append(
            {
                "$facet": {
                    "hits": [{"$count": "hits"}],
                    "consumers": [
                        {
                            "$group": {
                                "_id": None,
                                "consumers": {
                                    "$addToSet": "$metadata.request_details.origin",
                                },
                            }
                        }
                    ],
                    "two_xx_responses": [
                        {
                            "$match": {
                                "metadata.status_code": {
                                    "$gte": 200,
                                    "$lt": 300,
                                }
                            }
                        },
                        {"$count": "count"},
                    ],
                    "three_xx_responses": [
                        {
                            "$match": {
                                "metadata.status_code": {
                                    "$gte": 300,
                                    "$lt": 400,
                                }
                            }
                        },
                        {"$count": "count"},
                    ],
                    "four_xx_responses": [
                        {
                            "$match": {
                                "metadata.status_code": {
                                    "$gte": 400,
                                    "$lt": 500,
                                }
                            }
                        },
                        {"$count": "count"},
                    ],
                    "five_xx_responses": [
                        {"$match": {"metadata.status_code": {"$gte": 500}}},
                        {"$count": "count"},
                    ],
                }
            },
        )
        self.pipeline.append(
            {
                "$project": {
                    "consumers": {
                        "$size": {
                            "$ifNull": [
                                {"$arrayElemAt": ["$consumers.consumers", 0]},
                                [],
                            ]
                        },
                    },
                    "hits": {"$arrayElemAt": ["$hits.hits", 0]},
                    "two_xx_responses": {
                        "$arrayElemAt": ["$two_xx_responses.count", 0]
                    },
                    "three_xx_responses": {
                        "$arrayElemAt": ["$three_xx_responses.count", 0]
                    },
                    "four_xx_responses": {
                        "$arrayElemAt": ["$four_xx_responses.count", 0]
                    },
                    "five_xx_responses": {
                        "$arrayElemAt": ["$five_xx_responses.count", 0]
                    },
                }
            },
        )

        async for doc in db_client.analytics.aggregate(self.pipeline):
            return doc

    def _add_missing_timeseries_datapoints(
        self, results: List, periods_with_data: List
    ) -> List:
        if self.unit == "hour":
            for i in range(0, 25):
                hour = f"{i:02d}:00"
                if hour not in periods_with_data:
                    results.append({"period": hour, "hits": 0})
        else:
            start_date = self.start
            end_date = today

            delta = end_date - start_date  # returns timedelta

            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                day = day.date()
                if day.isoformat() not in periods_with_data:
                    results.append({"period": day.isoformat(), "hits": 0})

        return sorted(results, key=lambda d: d["period"])

    async def get_timeseries(self):
        self.pipeline.append(
            {
                "$group": {
                    "_id": {
                        "$dateTrunc": {
                            "date": "$request_time",
                            "unit": self.unit,
                        },
                    },
                    "hits": {"$sum": 1},
                },
            },
        )
        self.pipeline.append(
            {
                "$sort": {"_id": 1},
            },
        )

        results = []
        periods_with_data = []

        async for doc in db_client.analytics.aggregate(self.pipeline):
            doc["period"] = (
                doc.get("_id").date().isoformat()
                if self.unit == "day"
                else doc.get("_id").time().strftime("%H") + ":00"
            )
            periods_with_data.append(doc["period"])
            results.append(doc)

        results = self._add_missing_timeseries_datapoints(results, periods_with_data)

        return results

    async def get_breakdown(self):
        results = {
            "top_consumers": [],
            "top_platforms": [],
            "top_user_agents": [],
        }

        for key, inner_key, field in [
            ("top_consumers", "consumer", "$metadata.request_details.origin"),
            ("top_platforms", "platform", "$metadata.request_details.platform"),
            ("top_user_agents", "user_agent", "$metadata.request_details.user_agent"),
        ]:
            self.pipeline.append(
                {
                    "$group": {
                        "_id": field,
                        "hits": {"$count": {}},
                    },
                },
            )
            async for doc in db_client.analytics.aggregate(self.pipeline):
                doc[inner_key] = doc.get("_id")
                results.get(key).append(doc)
            self.pipeline.pop()
        return results


async def post_stats(stats: dict):
    await db_client.analytics.insert_one(stats)
