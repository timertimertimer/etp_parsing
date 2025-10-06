from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SAEnum, Index, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FileModelType(str, Enum):
    Auction = "Auction"
    Lot = "Lot"
    DebtorMessage = "DebtorMessage"
    LegalCase = "LegalCase"


class File(Base):
    __tablename__ = "files"
    __table_args__ = (Index("ix_model_type_model_id", "model_type", "model_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=True)
    model_type: Mapped[FileModelType] = mapped_column(
        SAEnum(FileModelType, convert_unicode=True)
    )
    model_id: Mapped[int] = mapped_column(Integer)
    is_image: Mapped[bool] = mapped_column(Boolean, default=False)
    is_image_from_archive: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<File(id={self.id}, name={self.name}, path={self.path}, url={self.url}, model_type={self.model_type}, model_id={self.model_id})>"
