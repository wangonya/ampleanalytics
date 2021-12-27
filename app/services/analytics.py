from datetime import datetime, timedelta

from app.services import db_client

today = datetime.now().replace(hour=0, minute=0, second=0)
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
                        "$size": {"$arrayElemAt": ["$consumers.consumers", 0]}
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

        async for doc in db_client.analytics.aggregate(self.pipeline):
            doc["date"] = doc.get("_id").isoformat()
            results.append(doc)

        return results


async def post_stats(stats: dict):
    await db_client.analytics.insert_one(stats)
