from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, DateTime, String, Integer, Float
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class StatusType(str, Enum):
    active = "active"
    disabled = "disabled"
    archived = "archived"


class ParserStatus(Base):
    __tablename__ = "parsers_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    trading_floor_id: Mapped[int] = mapped_column(ForeignKey("trading_floors.id"))
    status: Mapped[StatusType] = mapped_column(
        SAEnum(StatusType, convert_unicode=True), default=StatusType.disabled
    )
    counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
