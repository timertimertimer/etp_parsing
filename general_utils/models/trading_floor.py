from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from general_utils.models.base import Base


class TradingFloor(Base):
    __tablename__ = 'trading_floors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255))  # data_origin
    counterparty_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    counterparty = relationship("Counterparty", back_populates="trading_floor")
    auctions = relationship("Auction", back_populates="trading_floor", cascade="all, delete-orphan")
    status = relationship("ParserStatus", back_populates="trading_floor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TradingFloor(id={self.id}, name={self.name}, url={self.url})>"