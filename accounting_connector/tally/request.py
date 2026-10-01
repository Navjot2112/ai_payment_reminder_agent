class TallyXMLBuilder:
    """
    Builds XML requests for Tally.
    This class only creates XML strings.
    It does NOT send requests or parse responses.
    """

    def __init__(self, company_name: str):
        self.company_name = company_name

    def _build_xml(self, report_name: str) -> str:
        """
        Generic XML builder.
        Every request uses this method.
        """
        return f"""
<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export</TALLYREQUEST>
    </HEADER>

    <BODY>
        <DESC>

            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
            </STATICVARIABLES>

            <REPORTNAME>{report_name}</REPORTNAME>

        </DESC>
    </BODY>
</ENVELOPE>
""".strip()

    def build_test_connection_xml(self):
        """Build XML for testing the connection."""
        return self._build_xml("Test Connection")

    def build_fetch_companies_xml(self):
        """Build XML for fetching companies."""
        return self._build_xml("Companies")

    def build_fetch_customers_xml(self):
        """Build XML for fetching customers."""
        return self._build_xml("Customers")

    def build_fetch_vendors_xml(self):
        """Build XML for fetching vendors."""
        return self._build_xml("Vendors")

    def build_fetch_items_xml(self):
        """Build XML for fetching items."""
        return self._build_xml("Items")

    def build_fetch_ledgers_xml(self):
        """Build XML for fetching ledgers."""
        return self._build_xml("Ledgers")

    def build_fetch_sales_xml(self):
        """Build XML for fetching sales."""
        return self._build_xml("Sales")

    def build_fetch_purchases_xml(self):
        """Build XML for fetching purchases."""
        return self._build_xml("Purchases")