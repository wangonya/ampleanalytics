from typing import Optional

from pydantic import BaseModel


class Project(BaseModel):
    owner: str
    name: str
    description: str
