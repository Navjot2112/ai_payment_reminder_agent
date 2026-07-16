from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
import os

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

    # Round-trip test
    test_business_id = create_business("Sahib Industries", "+919417170517")
    print("Created test business with id:", test_business_id)

    save_message(
        business_id=test_business_id,
        customer_name="Sahib Traders",
        phone="+919417170517",
        direction="outgoing",
        message_text="Test message from SQLAlchemy setup",
    )

    history = get_history(test_business_id, "+919417170517")
    print(f"Found {len(history)} messages")
    for row in history:
        print(row)