from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("regions.id"))

    region = relationship(
        "Region", back_populates="cities", foreign_keys="[City.region_id]"
    )

    def __repr__(self):
        return (
            f"<City(id='{self.id}', name='{self.name}', region='{self.region.name}')>"
        )
