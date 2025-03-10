from datetime import datetime

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Float, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from general_utils.models.base import Base


class Lot(Base):
    __tablename__ = 'lots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ext_id: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    property_info: Mapped[str] = mapped_column(Text, nullable=True)
    price_start: Mapped[float] = mapped_column(Float)
    price_step: Mapped[float] = mapped_column(Float, nullable=True)
    auction_id: Mapped[int] = mapped_column(ForeignKey("auctions.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    auction = relationship("Auction", back_populates="lots")
    lot_periods = relationship("LotPeriod", back_populates="lot", cascade="all, delete-orphan")
    lot_category = relationship("LotCategory", back_populates="lot", cascade="all, delete-orphan")


class LotCategory(Base):
    __tablename__ = 'lot_categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(7))
    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id"))

    lot = relationship("Lot", back_populates="lot_category")
