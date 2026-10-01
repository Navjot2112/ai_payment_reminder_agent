import requests
from typing import Optional


class TallyClient:
    """
    Handles HTTP communication with the Tally server.

    Responsibilities:
    - Build the Tally URL
    - Send XML requests
    - Check whether the server is reachable

    This class does NOT:
    - Build XML
    - Parse XML
    - Contain business logic
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def build_url(self) -> str:
        """
        Build the Tally server URL.

        Example:
            http://localhost:9000
        """
        return f"http://{self.host}:{self.port}"

    def post(self, xml_request: str) -> Optional[str]:
        """
        Send an XML request to Tally.

        Args:
            xml_request: XML string.

        Returns:
            XML response string if successful,
            otherwise None.
        """
        try:
            response = requests.post(
                url=self.build_url(),
                data=xml_request,
                headers={
                    "Content-Type": "application/xml"
                },
                timeout=10,
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as e:
            print(f"Tally request failed: {e}")
            return None

    def is_server_running(self) -> bool:
        """
        Check whether the Tally server is reachable.

        Note:
        This is a temporary implementation.
        Later we'll send a small XML request instead
        of using HTTP GET.
        """
        try:
            response = requests.get(
                self.build_url(),
                timeout=5,
            )

            return response.ok

        except requests.RequestException as e:
            print(f"Tally server unavailable: {e}")
            return False