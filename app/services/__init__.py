import motor.motor_asyncio

from app.core.env import ENV

client = motor.motor_asyncio.AsyncIOMotorClient(ENV.MONGODB_URL)
db_client = client[ENV.MONGODB_DBNAME]
