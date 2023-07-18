from pydantic import BaseModel


class User(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    class Config:
        schema_extra = {
            "example": {
                'name': "John Doe",
                'description': "123 John Doe",
                'price': 123,
                'tax': 321,
            }
        }

class UpdateUser(User):
    id: str