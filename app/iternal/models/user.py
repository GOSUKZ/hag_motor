from pydantic import BaseModel


class User(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

    class Config:
        schema_extra = {
            "example": {
                'name': "John Doe",
                'description': "123 John Doe",
                'price': 123,
                'tax': 321,
            }
        }

class RegUser(BaseModel):
    login: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                'login': "admin",
                'password': "admin"
            }
        }

class UpdateUser(User):
    id: str