import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class EPTProvider(str, enum.Enum):
    worldline = "worldline"
    sumup = "sumup"
    other = "other"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, unique=True)
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)

    selling_points: Mapped[list["SellingPoint"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class SellingPoint(Base):
    __tablename__ = "selling_points"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    latitude: Mapped[float]
    longitude: Mapped[float]

    event: Mapped[Event] = relationship(back_populates="selling_points")
    epts: Mapped[list["EPT"]] = relationship(
        back_populates="selling_point", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="selling_point", cascade="all, delete-orphan"
    )


class EPT(Base):
    __tablename__ = "epts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    selling_point_id: Mapped[str] = mapped_column(
        ForeignKey("selling_points.id", ondelete="CASCADE")
    )
    provider: Mapped[EPTProvider] = mapped_column(Enum(EPTProvider))
    label: Mapped[str] = mapped_column(String)

    selling_point: Mapped[SellingPoint] = relationship(back_populates="epts")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="ept", cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("source", "source_row_hash", name="uix_source_hash"),
        Index("ix_transactions_event_occured", "event_id", "occurred_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    selling_point_id: Mapped[str] = mapped_column(
        ForeignKey("selling_points.id", ondelete="CASCADE")
    )
    ept_id: Mapped[str] = mapped_column(ForeignKey("epts.id", ondelete="CASCADE"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="CHF")
    occurred_at: Mapped[datetime] = mapped_column(DateTime)
    card_last4: Mapped[str] = mapped_column(String(4))
    source: Mapped[str] = mapped_column(String)
    source_row_hash: Mapped[str] = mapped_column(String)

    event: Mapped[Event] = relationship(back_populates="transactions")
    selling_point: Mapped[SellingPoint] = relationship(back_populates="transactions")
    ept: Mapped[EPT] = relationship(back_populates="transactions")
