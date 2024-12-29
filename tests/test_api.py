import unittest
import requests
import json
import time

class TestStateEndpoint(unittest.TestCase):
    BASE_URL = "http://host.docker.internal:8197"
    
    def setUp(self):
        # Set the state to RUNNING before testing
        url = f"{self.BASE_URL}/state"
        headers = {"Content-Type": "text/plain", "Accept": "text/plain"}
        response = requests.put(url, data="RUNNING", headers=headers)
        self.assertEqual(response.status_code, 200, "Failed to set state to RUNNING")

    def test_state_endpoint(self):
        """Test setting the state to RUNNING and validating the state."""
        # Make the request to the endpoint
        url = f"{self.BASE_URL}/state"
        response = requests.get(url)
        
        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Status code is not 200")

        # Assert the response body
        expected_response = "RUNNING"
        self.assertEqual(response.text.strip(), expected_response, f"Response is not '{expected_response}'")

    def test_request_endpoint(self):
        # Make the request to the /request endpoint
        url = f"{self.BASE_URL}/request"
        response = requests.get(url)
        
        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Status code is not 200")
        
        # Parse and validate the JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
        
        # Assert required keys in the response
        required_keys = [
            "Available Disk Space",
            "IP Address",
            "Running Processes",
            "Service",
            "Uptime (seconds)"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Key '{key}' not found in response")

        # Validate types of some keys
        self.assertIsInstance(data["Available Disk Space"], int, "'Available Disk Space' is not an integer")
        self.assertIsInstance(data["IP Address"], str, "'IP Address' is not a string")
        self.assertIsInstance(data["Running Processes"], list, "'Running Processes' is not a list")
        self.assertIsInstance(data["Service"], str, "'Service' is not a string")
        self.assertIsInstance(data["Uptime (seconds)"], str, "'Uptime (seconds)' is not a string")

        # Validate the structure of 'Running Processes'
        for process in data["Running Processes"]:
            self.assertIsInstance(process, dict, "Each process in 'Running Processes' should be a dictionary")
            self.assertIn("name", process, "Key 'name' not found in a process entry")
            self.assertIn("pid", process, "Key 'pid' not found in a process entry")
            self.assertIsInstance(process["name"], str, "Process 'name' should be a string")
            self.assertIsInstance(process["pid"], int, "Process 'pid' should be an integer")

    def test_init_state_endpoint(self):
        # Make the request to the endpoint
        url = f"{self.BASE_URL}/state"
        headers = {"Content-Type": "text/plain", "Accept": "text/plain"}
        response = requests.put(url, data="INIT", headers=headers)

        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Failed to reset state to INIT")

        # Assert the response body
        self.assertEqual(response.text.strip(), "State changed to INIT", "Unexpected response text when resetting state to INIT")

    def test_request_endpoint_after_init(self):
        # Set the state to INIT before testing /request endpoint
        self.test_init_state_endpoint()

        # Make the request to the /request endpoint
        url = f"{self.BASE_URL}/request"
        response = requests.get(url)

        # Assert the response status code
        self.assertEqual(response.status_code, 403, "Status code is not 403")

        # Assert the response body
        self.assertEqual(response.text.strip(), "Service not initialized", "Unexpected response when service is not initialized")

    def test_paused_state_endpoint(self):
        # Make the request to the endpoint
        url = f"{self.BASE_URL}/state"
        headers = {"Content-Type": "text/plain", "Accept": "text/plain"}
        response = requests.put(url, data="PAUSED", headers=headers)
        self.assertEqual(response.status_code, 200, "Failed to set state to PAUSED")
        response = requests.get(url)
        
        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Status code is not 200")

        # Assert the response body
        expected_response = "PAUSED"
        self.assertEqual(response.text.strip(), expected_response, f"Response is not '{expected_response}'")
    

    def test_request_endpoint_after_paused(self):
        # Set the state to PAUSED before testing /request endpoint
        self.test_paused_state_endpoint()

        # Allow time for state propagation
        time.sleep(1)

        # Make the request to the /request endpoint
        url = f"{self.BASE_URL}/request"
        response = requests.get(url)

        # Assert the response status code
        self.assertEqual(response.status_code, 503, "Status code is not 503")

        # Assert the response body
        expected_response = "Service unavailable"
        self.assertEqual(
            response.text.strip(),
            expected_response,
            f"Unexpected response: '{response.text.strip()}' (Expected: '{expected_response}')"
        )

    def test_running_state_endpoint(self):
        # Make the request to the endpoint
        url = f"{self.BASE_URL}/state"
        headers = {"Content-Type": "text/plain", "Accept": "text/plain"}
        response = requests.put(url, data="RUNNING", headers=headers)
        self.assertEqual(response.status_code, 200, "Failed to set state to RUNNING")
        response = requests.get(url)
        
        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Status code is not 200")

        # Assert the response body
        expected_response = "RUNNING"
        self.assertEqual(response.text.strip(), expected_response, f"Response is not '{expected_response}'")
    
    def test_request_after_running_again_endpoint(self):
        # Make the request to the /request endpoint
        url = f"{self.BASE_URL}/request"
        response = requests.get(url)
        
        # Assert the response status code
        self.assertEqual(response.status_code, 200, "Status code is not 200")
        
        # Parse and validate the JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
        
        # Assert required keys in the response
        required_keys = [
            "Available Disk Space",
            "IP Address",
            "Running Processes",
            "Service",
            "Uptime (seconds)"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Key '{key}' not found in response")

        # Validate types of some keys
        self.assertIsInstance(data["Available Disk Space"], int, "'Available Disk Space' is not an integer")
        self.assertIsInstance(data["IP Address"], str, "'IP Address' is not a string")
        self.assertIsInstance(data["Running Processes"], list, "'Running Processes' is not a list")
        self.assertIsInstance(data["Service"], str, "'Service' is not a string")
        self.assertIsInstance(data["Uptime (seconds)"], str, "'Uptime (seconds)' is not a string")

        # Validate the structure of 'Running Processes'
        for process in data["Running Processes"]:
            self.assertIsInstance(process, dict, "Each process in 'Running Processes' should be a dictionary")
            self.assertIn("name", process, "Key 'name' not found in a process entry")
            self.assertIn("pid", process, "Key 'pid' not found in a process entry")
            self.assertIsInstance(process["name"], str, "Process 'name' should be a string")
            self.assertIsInstance(process["pid"], int, "Process 'pid' should be an integer")

    def test_run_log(self):
        # Validate the run log
        run_log_url = f"{self.BASE_URL}/run-log"

        # Make a GET request to the run log endpoint
        run_log_response = requests.get(run_log_url)

        # Log the response details for debugging purposes
        print(f"Run log response status code: {run_log_response.status_code}")
        print(f"Run log response text:\n{run_log_response.text.strip()}")

        # Assert the response status code is 200 (OK)
        self.assertEqual(run_log_response.status_code, 200, "Run log endpoint failed")

        # Split the response text into individual log entries
        run_log_entries = run_log_response.text.strip().split("\n")

        # Assert that the run log is not empty
        self.assertTrue(len(run_log_entries) > 0, "Run log is empty")

        # Define the required state transitions
        required_transitions = {"INIT->RUNNING", "RUNNING->PAUSED", "PAUSED->RUNNING"}

        # Extract actual state transitions from the run log
        actual_transitions = {
            entry.split(": ")[1].strip()
            for entry in run_log_entries
            if "->" in entry
        }

        # Determine if any required transitions are missing
        missing_transitions = required_transitions - actual_transitions

        # Assert that all required transitions are present in the run log
        self.assertTrue(
            not missing_transitions,
            f"Missing transitions in run log: {missing_transitions}"
        )


if __name__ == "__main__":
    unittest.main()
