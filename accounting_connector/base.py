from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def connect(self):
        """Establish a connection to the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        """Terminate the connection to the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def test_connection(self):
        """Verify that the connector can successfully connect."""
        raise NotImplementedError

    @abstractmethod
    def fetch_companies(self):
        """Retrieve company records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def fetch_customers(self):
        """Retrieve customer records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def fetch_vendors(self):
        """Retrieve vendor records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def fetch_items(self):
        """Retrieve item/product records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def fetch_ledgers(self):
        """Retrieve ledger records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def fetch_sales(self):
        """Retrieve sales transaction records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def fetch_purchases(self):
        """Retrieve purchase transaction records from the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def create_invoice(self, invoice_data):
        """Create a new invoice in the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def create_customer(self, customer_data):
        """Create a new customer in the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def create_item(self, item_data):
        """Create a new item/product in the accounting system."""
        raise NotImplementedError

    @abstractmethod
    def sync_all(self):
        """Synchronize all relevant data with the accounting system."""
        raise NotImplementedError
