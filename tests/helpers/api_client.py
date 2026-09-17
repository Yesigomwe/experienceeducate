"""
Thin wrapper around the Flask test client for the attendance endpoint.

"""


class AttendanceApiClient:
    ENDPOINT = "/api/v1/attendance"

    def __init__(self, flask_test_client):
        self._client = flask_test_client

    def submit(self, payload):
        return self._client.post(
            self.ENDPOINT,
            json=payload,
        )
