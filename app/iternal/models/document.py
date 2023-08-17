from pydantic import BaseModel
from typing import Optional


class Document(BaseModel):
    date: str
    place_sending: str
    type: str
    phone: str
    code: str
    description: str
    coount: int
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
    coount: Optional[int]
    weight: Optional[float]
    space: Optional[float]
    density: Optional[float]
    place_delivery: Optional[str]
    packaging: Optional[float]
    delivery: Optional[float]
    other: Optional[float]
    insurance: Optional[int]
    unit_price: Optional[float]
    total: Optional[float]
    arrival_date: Optional[str]
    received_positions: Optional[str]


class UpdateDocumentManagerO(BaseModel):
    date: Optional[str]
    place_sending: Optional[str]
    type: Optional[str]
    phone: Optional[str]
    code: Optional[str]
    description: Optional[str]
    coount: Optional[int]
    weight: Optional[float | str]
    space: Optional[float | str]
    density: Optional[float | str]
    place_deivery: Optional[str | str]
    packaging: Optional[float | str]
    delivery: Optional[float | str]
    other: Optional[float | str]
    insurance: Optional[int | str]
    unit_price: Optional[float | str]
    total: Optional[float | str]


class UpdateDocumentManagerI(BaseModel):
    arrival_date: Optional[str]
    received_positions: Optional[str]