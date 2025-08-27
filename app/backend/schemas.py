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


# Transactions / Imports
class TransactionIn(BaseModel):
    selling_point_name: str
    ept_label: Optional[str] = None
    amount_cents: int
    currency: str
    occurred_at: datetime
    card_last4: str
    source_row_hash: str


class ImportSummary(BaseModel):
    processed: int
    inserted: int
    skipped_duplicates: int
    errors: int


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


# Timeline schemas
class TimelineSeries(BaseModel):
    selling_point_id: str
    lat: float
    lng: float
    cumulative: List[int]


class TimelineEvent(BaseModel):
    start_at: datetime
    end_at: datetime


class EventTimeline(BaseModel):
    event: TimelineEvent
    buckets: List[datetime]
    series: List[TimelineSeries]
