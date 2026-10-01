
import TallyClient 

class TallyConnector(BaseConnector):
   
    
    def __init__(self, host, port, company_name, username, password):
        super().__init__()
        self.host = host
        self.port = port
        self.client = TallyClient(host, port)
        self.company_name = company_name
        self.username = username
        self.password = password
        self.connected = False

    def connect(self):
        if self.client.is_server_running():
            self.connected = True
            return True
        else:
            self.connected = False
            return False

    def disconnect(self):
        self.connected = False

    def test_connection(self):
        return self.connect()
        
    def fetch_companies(self):
        pass
    def fetch_customers(self):
        pass
    def fetch_vendors(self):
        pass
    def fetch_items(self):
        pass                
    def fetch_ledgers(self):
        pass
    def fetch_sales(self):
        pass
    def fetch_purchases(self):
        pass
    def create_invoice(self, invoice_data):
        pass
    def create_customer(self, customer_data):
        pass
    def create_item(self, item_data):
        pass
    def sync_all(self):
        pass