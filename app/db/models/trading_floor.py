import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql.functions import func

from .base import Base


class StatusType(str, Enum):
    active = "active"
    disabled = "disabled"
    archived = "archived"


class TradingFloor(Base):
    __tablename__ = "trading_floors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255))  # data_origin
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    status: Mapped[StatusType] = mapped_column(
        SAEnum(StatusType, convert_unicode=True), default=StatusType.disabled
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    counterparty = relationship("Counterparty", back_populates="trading_floor")
    auctions = relationship(
        "Auction", back_populates="trading_floor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TradingFloor(id={self.id}, name={self.name}, url={self.url})>"
