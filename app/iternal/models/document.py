from pydantic import BaseModel
from typing import Optional, Union


class Document(BaseModel):
    date: str
    place_sending: str
    type: str
    phone: str
    code: str
    description: str
    count: int
    weight: float
    space: float
    density: float
    place_delivery: str
    packaging: float
    delivery: float
    other: float
    insurance: int
    unit_price: float
    total: float
    arrival_date: str
    received_positions: str


class DBDocument(Document):
    _id: str
    date: str
    log_colection: list
    created_at: str
    updated_at: str


class UpdateDocument(BaseModel):
    date: Optional[str]
    place_sending: Optional[str]
    type: Optional[str]
    phone: Optional[str]
    code: Optional[str]
    description: Optional[str]
    count: Optional[int]
    weight: Optional[float]
    space: Optional[float]
    density: Optional[float]
    place_delivery: Optional[str]
    packaging: Optional[Union[float, str]]
    delivery: Optional[Union[float, str]]
    other: Optional[Union[float, str]]
    insurance: Optional[Union[int, str]]
    unit_price: Optional[Union[float, str]]
    total: Optional[Union[float, str]]
    arrival_date: Optional[Union[float, str]]
    received_positions: Optional[Union[float, str]]


class UpdateDocumentManagerO(BaseModel):
    date: Optional[str]
    place_sending: Optional[str]
    type: Optional[str]
    phone: Optional[str]
    code: Optional[str]
    description: Optional[str]
    count: Optional[int]
    weight: Optional[Union[float, str]]
    space: Optional[Union[float, str]]
    density: Optional[Union[float, str]]
    place_delivery: Optional[str]
    packaging: Optional[Union[float, str]]
    delivery: Optional[Union[float, str]]
    other: Optional[Union[float, str]]
    insurance: Optional[Union[int, str]]
    unit_price: Optional[Union[float, str]]
    total: Optional[Union[float, str]]


class UpdateDocumentManagerI(BaseModel):
    arrival_date: Optional[str]
    received_positions: Optional[str]