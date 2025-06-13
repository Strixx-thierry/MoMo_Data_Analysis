from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
from datetime import datetime
import re
from typing import List
import json

from database import get_db, engine
import models
from models import Transaction, TransactionType

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MTN MoMo SMS Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_amount(text: str) -> float:
    """Extract amount from text."""
    match = re.search(r'(\d+(?:\.\d+)?)\s*RWF', text)
    return float(match.group(1)) if match else 0.0

def parse_transaction_id(text: str) -> str:
    """Extract transaction ID from text."""
    match = re.search(r'Transaction ID:\s*(\d+)', text)
    return match.group(1) if match else None

def categorize_transaction(text: str) -> TransactionType:
    """Categorize transaction based on message content."""
    text = text.lower()
    if "you have received" in text:
        return TransactionType.INCOMING_MONEY
    elif "payment" in text and "completed" in text and "airtime" not in text and "cash power" not in text:
        return TransactionType.PAYMENT
    elif "transfer" in text:
        return TransactionType.TRANSFER
    elif "bank deposit" in text:
        return TransactionType.BANK_DEPOSIT
    elif "airtime" in text:
        return TransactionType.AIRTIME
    elif "cash power" in text:
        return TransactionType.CASH_POWER
    elif "ltd" in text:
        return TransactionType.THIRD_PARTY
    elif "withdrawn" in text:
        return TransactionType.WITHDRAWAL
    elif any(word in text for word in ['bundle', 'internet', 'data', 'voice']):
        return TransactionType.BUNDLE
    else:
        return TransactionType.OTHER

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process XML file."""
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Only XML files are allowed")
    
    content = await file.read()
    try:
        tree = ET.fromstring(content)
    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Invalid XML file")
    
    transactions = []
    for sms in tree.findall("sms"):
        body = sms.get("body", "")
        if not body:
            continue
            
        transaction = Transaction(
            transaction_type=categorize_transaction(body),
            amount=parse_amount(body),
            transaction_id=parse_transaction_id(body),
            message=body,
            timestamp=datetime.now(),  # You might want to parse this from the message
            status="completed"
        )
        transactions.append(transaction)
    
    db.add_all(transactions)
    db.commit()
    
    return {"message": f"Successfully processed {len(transactions)} transactions"}

@app.get("/transactions/")
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_type: TransactionType = None,
    db: Session = Depends(get_db)
):
    """Get transactions with optional filtering."""
    query = db.query(Transaction)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    return query.offset(skip).limit(limit).all()

@app.get("/statistics/")
def get_statistics(db: Session = Depends(get_db)):
    """Get transaction statistics."""
    total_transactions = db.query(Transaction).count()
    total_amount = db.query(func.sum(Transaction.amount)).scalar() or 0
    
    type_stats = db.query(
        Transaction.transaction_type,
        func.count(Transaction.id),
        func.sum(Transaction.amount)
    ).group_by(Transaction.transaction_type).all()
    
    return {
        "total_transactions": total_transactions,
        "total_amount": total_amount,
        "type_statistics": [
            {
                "type": stat[0].value,
                "count": stat[1],
                "amount": stat[2] or 0
            }
            for stat in type_stats
        ]
    } 