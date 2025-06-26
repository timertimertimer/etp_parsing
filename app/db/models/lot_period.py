from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LotPeriod(Base):
    __tablename__ = "lot_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_start_at: Mapped[datetime] = mapped_column(DateTime)
    request_end_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    trading_start_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    trading_end_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    price: Mapped[float] = mapped_column(Float)

    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lot = relationship("Lot", back_populates="lot_periods")
