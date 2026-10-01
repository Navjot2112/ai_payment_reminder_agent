from app.accounting_connector.manager import ConnectionManager


class ConnectorService:
    """Service for managing accounting connector connections."""

    def __init__(self):
        self.manager = ConnectionManager()
        # Later:
        # self.storage = ConnectorStorage()

    def create_connection(self, data):
        """Save connection in DB."""
        # return self.storage.create(data)
        pass

    def update_connection(self, connector_id, data):
        """Update existing connection."""
        # return self.storage.update(connector_id, data)
        pass

    def delete_connection(self, connector_id):
        """Delete connection."""
        # return self.storage.delete(connector_id)
        pass

    def get_connection(self, connector_id):
        """Get one connection."""
        # return self.storage.get_by_id(connector_id)
        pass

    def get_all_connections(self):
        """Return all saved connections."""
        # return self.storage.get_all()
        pass

    def test_connection(self, connector_id):
        """
        Flow:
        Get config from DB
        -> Get connector from manager
        -> Test connection
        """
        # config = self.storage.get_by_id(connector_id)
        # connector = self.manager.get_connector(config.connector_name)
        # return connector.test_connection()
        pass

    def sync_connection(self, connector_id):
        """
        Flow:
        Get config
        -> Get connector
        -> Sync everything
        """
        # config = self.storage.get_by_id(connector_id)
        # connector = self.manager.get_connector(config.connector_name)
        # return connector.sync_all()
        pass