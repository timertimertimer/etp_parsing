from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LegalCase(Base):
    __tablename__ = "legal_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(255), nullable=True)
    court_name: Mapped[str] = mapped_column(String(255), nullable=True)
    debtor_category: Mapped[str] = mapped_column(String(255), nullable=True)
    fedresurs_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    auctions = relationship("Auction", back_populates="legal_case")
    debtor_messages = relationship("DebtorMessage", back_populates="legal_case")

    def __repr__(self):
        return f"<LegalCase(id={self.id}, number={self.number})>"
