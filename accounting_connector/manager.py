class ConnectionManager:
    _CONNECTORS = {
        "tally": TallyConnector,
        "zoho": ZohoConnector,
        "busy": BusyConnector,
        "quickbooks": QuickBooksConnector,
    }

    def get_connector(self, connector_name: str):
        connector_class = self._CONNECTORS.get(connector_name.lower())
        if not connector_class:
            raise ValueError(f"Connector '{connector_name}' not found.")
        return connector_class()

    def list_supported_connectors(self):
        return list(self._CONNECTORS.keys())

    def is_supported(self, connector_name: str):
        return connector_name.lower() in self._CONNECTORS