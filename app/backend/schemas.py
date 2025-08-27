from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .models import EPTProvider


# Event
class EventBase(BaseModel):
    name: str
    start_at: datetime
    end_at: datetime


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class EventRead(EventBase):
    id: str

    class Config:
        orm_mode = True


# SellingPoint
class SellingPointBase(BaseModel):
    name: str
    latitude: float
    longitude: float


class SellingPointCreate(SellingPointBase):
    pass


class SellingPointUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SellingPointRead(SellingPointBase):
    id: str
    event_id: str

    class Config:
        orm_mode = True


# EPT
class EPTBase(BaseModel):
    provider: EPTProvider
    label: str


class EPTCreate(EPTBase):
    pass


class EPTUpdate(BaseModel):
    provider: Optional[EPTProvider] = None
    label: Optional[str] = None


class EPTRead(EPTBase):
    id: str
    selling_point_id: str

    class Config:
        orm_mode = True


# Summary schemas
class EPTSummary(BaseModel):
    id: str
    label: str
    total_cents: int


class SellingPointSummary(BaseModel):
    id: str
    name: str
    total_cents: int
    epts: List[EPTSummary]


class EventSummary(BaseModel):
    event_id: str
    selling_points: List[SellingPointSummary]
