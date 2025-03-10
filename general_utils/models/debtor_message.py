from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from general_utils.models.base import Base


class DebtorMessage(Base):
    __tablename__ = 'debtor_messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(255), unique=True)
    type: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(MEDIUMTEXT, nullable=True)
    fedresurs_url: Mapped[str] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    debtor_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"), nullable=False)

    debtor = relationship("Counterparty", back_populates="debtor_messages")
