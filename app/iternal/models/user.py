from pydantic import BaseModel
from typing import Optional

class LoginUser(BaseModel):
    login: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                'login': "admin",
                'password': "admin"
            }
        }

class RegUser(BaseModel):
    login: str
    password: str

    role: int = 0
    company_key: list = []

    class Config:
        schema_extra = {
            "example": {
                'login': "admin",
                'password': "admin"
            }
        }


class ChangeUser(BaseModel):
    login: str

    password: Optional[str]
    role: Optional[int]
    company_key: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                'login': "admin",
                'password': "admin"
            }
        }
