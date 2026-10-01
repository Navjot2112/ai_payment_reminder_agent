from fastapi import APIRouter

from app.accounting_connector.schemas import (
    ConnectorCreate,
    ConnectorUpdate,
)

from app.accounting_connector.service import ConnectorService


router = APIRouter(
    prefix="/api/connectors",
    tags=["Accounting Connectors"]
)

service = ConnectorService()


@router.post("/")
def create_connection(payload: ConnectorCreate):
    return service.create_connection(payload)


@router.get("/")
def get_all_connections():
    return service.get_all_connections()


@router.get("/{connector_id}")
def get_connection(connector_id: int):
    return service.get_connection(connector_id)


@router.put("/{connector_id}")
def update_connection(
    connector_id: int,
    payload: ConnectorUpdate,
):
    return service.update_connection(connector_id, payload)


@router.delete("/{connector_id}")
def delete_connection(connector_id: int):
    return service.delete_connection(connector_id)


@router.post("/{connector_id}/test")
def test_connection(connector_id: int):
    return service.test_connection(connector_id)


@router.post("/{connector_id}/sync")
def sync_connection(connector_id: int):
    return service.sync_connection(connector_id)