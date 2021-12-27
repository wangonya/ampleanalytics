from typing import List

from pydantic import BaseSettings


class Env(BaseSettings):
    HOST: str
    PORT: int
    ALLOWED_ORIGINS: List[str]

    # db
    MONGODB_URL: str
    MONGODB_DBNAME: str

    class Config:
        case_sensitive = True
        env_file = ".env"


ENV = Env()
