import requests

def test_state_api():
    response = requests.get("http://localhost:8197/state")
    assert response.status_code == 200
    assert response.text in ["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]

def test_request_api():
    response = requests.get("http://localhost:8197/request")
    assert response.status_code == 200
