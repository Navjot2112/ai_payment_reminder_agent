from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Date, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
import os
from datetime import datetime as _dt

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    owner_phone = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    messages = relationship("Message", back_populates="business")


class Promise(Base):
    __tablename__ = "promises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_name = Column(String)
    phone = Column(String)
    promised_date = Column(DateTime)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_name = Column(String)
    phone = Column(String)
    direction = Column(String)
    message_text = Column(String)
    classification = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

    business = relationship("Business", back_populates="messages")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    invoice_no = Column(String)
    amount = Column(Numeric, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="unpaid")
    reminder_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class PendingApproval(Base):
    __tablename__ = "pending_approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_name = Column(String)
    phone = Column(String)
    question_text = Column(String)
    owner_response = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())

def save_pending_approval(business_id, customer_name, phone, question_text):
    session = SessionLocal()
    try:
        approval = PendingApproval(
            business_id=business_id,
            customer_name=customer_name,
            phone=phone.replace("+", ""),
            question_text=question_text,
        )
        session.add(approval)
        session.commit()
        session.refresh(approval)
        return approval.id
    finally:
        session.close()


def get_pending_approvals(business_id):
    session = SessionLocal()
    try:
        rows = (
            session.query(PendingApproval)
            .filter(PendingApproval.business_id == business_id, PendingApproval.status == "pending")
            .order_by(PendingApproval.created_at.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "customer_name": r.customer_name,
                "phone": r.phone,
                "question_text": r.question_text,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    finally:
        session.close()


def resolve_pending_approval(approval_id, owner_response):
    session = SessionLocal()
    try:
        approval = session.query(PendingApproval).filter(PendingApproval.id == approval_id).first()
        if approval:
            approval.owner_response = owner_response
            approval.status = "resolved"
            session.commit()
            return {"phone": approval.phone, "customer_name": approval.customer_name}
        return None
    finally:
        session.close()

def create_tables():
    Base.metadata.create_all(engine)
    print("Database and tables ready.")


def save_message(business_id, customer_name, phone, direction, message_text, classification=None):
    session = SessionLocal()
    try:
        msg = Message(
            business_id=business_id,
            customer_name=customer_name,
            phone=phone.replace("+", ""),
            direction=direction,
            message_text=message_text,
            classification=classification,
        )
        session.add(msg)
        session.commit()
    finally:
        session.close()


def save_promise(business_id, customer_name, phone, promised_date, status="pending"):
    session = SessionLocal()
    try:
        promise = Promise(
            business_id=business_id,
            customer_name=customer_name,
            phone=phone.replace("+", ""),
            promised_date=promised_date,
            status=status,
        )
        session.add(promise)
        session.commit()
        session.refresh(promise)
        return promise.id
    finally:
        session.close()


def save_invoice(business_id, customer_name, phone, invoice_no, amount, due_date, status="unpaid"):
    if isinstance(due_date, str):
        due_date = _dt.strptime(due_date, "%Y-%m-%d").date()
    session = SessionLocal()
    try:
        invoice = Invoice(
            business_id=business_id,
            customer_name=customer_name,
            phone=phone.replace("+", ""),
            invoice_no=invoice_no,
            amount=amount,
            due_date=due_date,
            status=status,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        return invoice.id
    finally:
        session.close()


def get_invoices(business_id):
    session = SessionLocal()
    try:
        rows = (
            session.query(Invoice)
            .filter(Invoice.business_id == business_id)
            .order_by(Invoice.due_date.asc())
            .all()
        )
        return [
            {
                "id": r.id,
                "customer_name": r.customer_name,
                "phone": r.phone,
                "invoice_no": r.invoice_no,
                "amount": float(r.amount),
                "due_date": r.due_date.isoformat(),
                "status": r.status,
                "reminder_count": r.reminder_count or 0,
            }
            for r in rows
        ]
    finally:
        session.close()


def update_invoice_status(invoice_id, status):
    session = SessionLocal()
    try:
        invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            invoice.status = status
            session.commit()
    finally:
        session.close()


def increment_reminder_count(invoice_id):
    session = SessionLocal()
    try:
        invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            invoice.reminder_count = (invoice.reminder_count or 0) + 1
            session.commit()
            return invoice.reminder_count
        return 0
    finally:
        session.close()


def get_history(business_id, phone):
    phone = phone.replace("+", "")
    session = SessionLocal()
    try:
        rows = (
            session.query(Message)
            .filter(Message.business_id == business_id, Message.phone == phone)
            .order_by(Message.timestamp.asc())
            .all()
        )
        return [
            (r.direction, r.message_text, r.classification, r.timestamp)
            for r in rows
        ]
    finally:
        session.close()


def get_all_messages(business_id=None):
    session = SessionLocal()
    try:
        query = session.query(Message)
        if business_id is not None:
            query = query.filter(Message.business_id == business_id)
        rows = query.all()
        return [
            (r.id, r.business_id, r.customer_name, r.phone, r.direction,
             r.message_text, r.classification, r.timestamp)
            for r in rows
        ]
    finally:
        session.close()


def create_business(name, owner_phone):
    session = SessionLocal()
    try:
        business = Business(name=name, owner_phone=owner_phone)
        session.add(business)
        session.commit()
        session.refresh(business)
        return business.id
    finally:
        session.close()


if __name__ == "__main__":
    create_tables()
    print("Tables created/verified.")