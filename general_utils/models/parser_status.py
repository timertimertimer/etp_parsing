from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, DateTime, String, Integer, Float
from sqlalchemy.orm import mapped_column, relationship, Mapped

from general_utils.models.base import Base
from sqlalchemy import Enum as SAEnum


class StatusType(str, Enum):
    active = "active"
    disabled = "disabled"
    archived = "archived"


class ParserStatus(Base):
    __tablename__ = 'parsers_status'

    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    trading_floor_id: Mapped[int] = mapped_column(ForeignKey("trading_floors.id"))
    status: Mapped[StatusType] = mapped_column(SAEnum(StatusType, convert_unicode=True), default=StatusType.disabled)
    counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trading_floor = relationship('TradingFloor', back_populates="status")
