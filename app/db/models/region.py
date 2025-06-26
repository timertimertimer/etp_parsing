from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    oktmo: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(255))

    addresses = relationship("Address", back_populates="region")
    cities = relationship("City", back_populates="region")

    def __repr__(self):
        return f"<Region(id={self.id}, name={self.name}, oktmo={self.oktmo})>"
