from pydantic import BaseModel
from typing import Optional


class Company(BaseModel):
    company_key: str