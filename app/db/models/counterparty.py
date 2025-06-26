from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from enum import Enum
from sqlalchemy import Enum as SAEnum


class CounterpartyType(str, Enum):
    individual = "individual"
    legal_entity = "legal_entity"


class Counterparty(Base):
    __tablename__ = "counterparties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inn: Mapped[str] = mapped_column(String(12), nullable=True, unique=True)
    kpp: Mapped[str] = mapped_column(String(9), nullable=True)
    snils: Mapped[str] = mapped_column(String(11), nullable=True)
    ogrn: Mapped[str] = mapped_column(String(13), nullable=True)
    ogrnip: Mapped[str] = mapped_column(String(15), nullable=True)
    okopf: Mapped[int] = mapped_column(String(5), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    short_name: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=True)
    fedresurs_url: Mapped[str] = mapped_column(String(255), nullable=True)
    type: Mapped[CounterpartyType] = mapped_column(
        SAEnum(CounterpartyType, convert_unicode=True), nullable=True
    )
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    organized_auctions = relationship(
        "Auction",
        back_populates="organizer",
        foreign_keys="[Auction.organizer_id]",
    )
    arbitrated_auctions = relationship(
        "Auction",
        back_populates="arbitrator",
        foreign_keys="[Auction.arbitrator_id]",
    )
    debtor_auctions = relationship(
        "Auction", back_populates="debtor", foreign_keys="[Auction.debtor_id]"
    )
    address = relationship("Address", back_populates="counterparty")
    trading_floor = relationship("TradingFloor", back_populates="counterparty")
    sro_memberships = relationship(
        "CounterpartySRO",
        back_populates="counterparty",
        foreign_keys="[CounterpartySRO.counterparty_id]",
    )
    sro_affiliations = relationship(
        "CounterpartySRO",
        back_populates="sro",
        foreign_keys="[CounterpartySRO.sro_id]",
    )
    debtor_messages = relationship("DebtorMessage", back_populates="debtor")

    def __repr__(self):
        return f"<Counterparty(id={self.id}, inn={self.inn}, name={self.name}, short_name={self.short_name})>"


class CounterpartySRO(Base):
    __tablename__ = "counterparty_sro"
    __table_args__ = (PrimaryKeyConstraint("counterparty_id", "sro_id"),)

    counterparty_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"))
    sro_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"))
    message_number: Mapped[str] = mapped_column(String(255), nullable=True)
    activity_type: Mapped[str] = mapped_column(Text, nullable=True)
    entered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True
    )

    counterparty = relationship("Counterparty", foreign_keys=[counterparty_id])
    sro = relationship("Counterparty", foreign_keys=[sro_id])

    def __repr__(self):
        return f"<CounterpartySRO(counterparty_id={self.counterparty_id}, sro_id={self.sro_id})>"
