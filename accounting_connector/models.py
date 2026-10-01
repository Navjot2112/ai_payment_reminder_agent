from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
)

from app.database.database import Base


class ConnectorConfig(Base):
    __tablename__ = "connector_configs"

    id = Column(Integer, primary_key=True, index=True)

    connector_name = Column(String(50), nullable=False)

    host = Column(String(255), nullable=False, default="localhost")

    port = Column(Integer, nullable=False)

    username = Column(String(255), nullable=True)

    password = Column(String(255), nullable=True)

    company_name = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)

    last_sync = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )