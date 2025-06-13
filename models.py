from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class TransactionType(enum.Enum):
    INCOMING_MONEY = "incoming_money"
    PAYMENT = "payment"
    TRANSFER = "transfer"
    BANK_DEPOSIT = "bank_deposit"
    AIRTIME = "airtime"
    CASH_POWER = "cash_power"
    THIRD_PARTY = "third_party"
    WITHDRAWAL = "withdrawal"
    BANK_TRANSFER = "bank_transfer"
    BUNDLE = "bundle"
    OTHER = "other"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(Enum(TransactionType))
    amount = Column(Float)
    sender = Column(String)
    recipient = Column(String)
    transaction_id = Column(String, unique=True)
    timestamp = Column(DateTime)
    message = Column(String)
    fee = Column(Float, nullable=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 