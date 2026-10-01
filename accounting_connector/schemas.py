from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConnectorCreate(BaseModel):
    connector_name: str = Field(..., title="Connector name")
    host: str = Field(..., title="Host address")
    port: int = Field(..., title="Port")
    username: str = Field(..., title="Username")
    password: str = Field(..., title="Password")
    company_name: str = Field(..., title="Company name")


class ConnectorUpdate(BaseModel):
    connector_name: Optional[str] = Field(None, title="Connector name")
    host: Optional[str] = Field(None, title="Host address")
    port: Optional[int] = Field(None, title="Port")
    username: Optional[str] = Field(None, title="Username")
    password: Optional[str] = Field(None, title="Password")
    company_name: Optional[str] = Field(None, title="Company name")


class ConnectorResponse(BaseModel):
    id: int
    connector_name: str
    host: str
    port: int
    company_name: str
    is_active: bool
    last_sync: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
