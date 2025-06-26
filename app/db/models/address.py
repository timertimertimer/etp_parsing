from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    region_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("regions.id"), nullable=True
    )

    region = relationship(
        "Region",
        back_populates="addresses",
        foreign_keys="[Address.region_id]",
    )
    counterparty = relationship(
        "Counterparty",
        back_populates="address",
        foreign_keys="[Counterparty.address_id]",
    )

    def __repr__(self):
        return (
            f"<Address(id={self.id}, name='{self.name}', region_id='{self.region_id}')>"
        )
