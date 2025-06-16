from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from sqlalchemy import Enum as SAEnum


class AuctionType(str, Enum):
    auction = "auction"
    competition = "competition"
    offer = "offer"


class FormType(str, Enum):
    open = "open"
    closed = "closed"


class Auction(Base):
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    ext_id: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255), unique=True)
    number: Mapped[str] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(
        SAEnum(AuctionType, convert_unicode=True)
    )
    form: Mapped[str] = mapped_column(SAEnum(FormType, convert_unicode=True))
    message_number: Mapped[str] = mapped_column(String(255), nullable=True)
    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    arbitrator_id: Mapped[int] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    debtor_id: Mapped[int] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    trading_floor_id: Mapped[int] = mapped_column(
        ForeignKey("trading_floors.id")
    )
    legal_case_id: Mapped[int] = mapped_column(
        ForeignKey("legal_cases.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    organizer = relationship(
        "Counterparty",
        back_populates="organized_auctions",
        foreign_keys="[Auction.organizer_id]",
    )
    arbitrator = relationship(
        "Counterparty",
        back_populates="arbitrated_auctions",
        foreign_keys="[Auction.arbitrator_id]",
    )
    debtor = relationship(
        "Counterparty",
        back_populates="debtor_auctions",
        foreign_keys="[Auction.debtor_id]",
    )
    trading_floor = relationship("TradingFloor", back_populates="auctions")
    lots = relationship("Lot", back_populates="auction", cascade="all, delete")
    legal_case = relationship("LegalCase", back_populates="auctions")

    def __repr__(self):
        return f"<Auction(id={self.id}, number={self.number})>"
