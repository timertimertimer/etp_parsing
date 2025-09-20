from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from sqlalchemy import Enum as SAEnum


class AuctionPropertyType(str, Enum):
    bankruptcy = "bankruptcy"

    arrested = "arrested"

    commercial = "commercial"

    legal_entities = "legal_entities"
    fz44 = "fz44"
    capital_repair = "capital_repair"

    fz223 = "fz223"

    rent = "rent"

    gis = "gis"

    def __str__(self):
        return self.value


class AuctionType(str, Enum):
    auction = "auction"
    competition = "competition"
    offer = "offer"
    pdo = "pdo"
    rfp = "rfp"
    tender = "tender"
    reduction = "reduction"


class FormType(str, Enum):
    open = "open"
    closed = "closed"


class Auction(Base):
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    property_type: Mapped[str] = mapped_column(
        SAEnum(AuctionPropertyType), nullable=True
    )
    ext_id: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255), unique=True)
    number: Mapped[str] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(
        SAEnum(AuctionType, convert_unicode=True), nullable=True
    )
    form: Mapped[str] = mapped_column(SAEnum(FormType, convert_unicode=True))
    message_number: Mapped[str] = mapped_column(String(255), nullable=True)
    # bid_security: Mapped[float] = mapped_column(Float, nullable=True)
    # performace_security: Mapped[float] = mapped_column(Float, nullable=True)
    # operators_fee: Mapped[float] = mapped_column(Float, nullable=True)
    # execution_time: Mapped[str] = mapped_column(String, nullable=True)
    # subject_info = ...
    # sme: Mapped[bool] = mapped_column(Boolean, default=False)

    organizer_id: Mapped[int | None] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    arbitrator_id: Mapped[int | None] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    debtor_id: Mapped[int | None] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True
    )
    trading_floor_id: Mapped[int] = mapped_column(ForeignKey("trading_floors.id"))
    legal_case_id: Mapped[int | None] = mapped_column(
        ForeignKey("legal_cases.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
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
