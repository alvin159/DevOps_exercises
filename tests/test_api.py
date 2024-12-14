import unittest
import requests

class TestStateEndpoint(unittest.TestCase):
    def test_state_endpoint(self):
        # Make the request to the endpoint
        url = "http://localhost:8197/state"
        response = requests.get(url)
        print(response)
        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Status code is not 200")

        # Assert the response body
        expected_response = "RUNNING"
        self.assertEqual(response.text.strip(), expected_response, f"Response is not '{expected_response}'")

if __name__ == "__main__":
    unittest.main()
