from datetime import datetime

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from general_utils.models.base import Base


class Lot(Base):
    __tablename__ = 'lots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ext_id: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    property_info: Mapped[str] = mapped_column(Text, nullable=True)
    price_start: Mapped[float] = mapped_column(Float)
    price_step: Mapped[float] = mapped_column(Float, nullable=True)
    auction_id: Mapped[int] = mapped_column(ForeignKey("auctions.id"))
    category: Mapped[str] = mapped_column(String(255), nullable=True)
    # category_id: Mapped[int] = mapped_column(ForeignKey("lot_categories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    auction = relationship("Auction", back_populates="lots")
    lot_periods = relationship("LotPeriod", back_populates="lot", cascade="all, delete-orphan")


# class LotCategories(Base):
#     __tablename__ = 'lot_categories'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(255))
#
#     lots = relationship("Lot", back_populates="category", foreign_keys="[Lot.category_id]")
