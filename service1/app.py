from flask import Flask, request, jsonify
import logging
import datetime
import os
import psutil

app = Flask(__name__)

# State management
state = {"current": "INIT"}
state_log = []

# Logger setup
logging.basicConfig(filename='state_changes.log', level=logging.INFO, format='%(asctime)s: %(message)s')

def log_state_change(prev, new):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp}: {prev}->{new}"
    state_log.append(log_entry)
    logging.info(log_entry)

@app.route('/state', methods=['PUT'])
def update_state():
    global state
    content_type = request.content_type

    if content_type == "text/plain":
        new_state = request.data.decode('utf-8')  # Decode plain text payload
    elif content_type == "application/json":
        new_state = request.get_json().get('state')  # Handle JSON payload
    else:
        return "Unsupported Media Type", 415

    if new_state not in ["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]:
        return jsonify({"error": "Invalid state"}), 400

    prev_state = state["current"]
    if new_state == prev_state:
        return "State unchanged", 200

    # Update state
    state["current"] = new_state
    log_state_change(prev_state, new_state)

    # Handle special cases
    if new_state == "INIT":
        state_log.clear()
    elif new_state == "SHUTDOWN":
        logging.info("System is shutting down...")
        # Code to stop all containers can be triggered here

    return f"State changed to {new_state}", 200


@app.route('/state', methods=['GET'])
def get_state():
    return state["current"], 200

@app.route('/request', methods=['GET'])
def request_service():
    if state["current"] == "PAUSED":
        return "Service unavailable", 503
    return "Service response: OK", 200

@app.route('/run-log', methods=['GET'])
def get_run_log():
    return "\n".join(state_log), 200

@app.route('/api', methods=['GET'])
def get_service_info():
    try:
        # Check the current state of the system
        current_state = state["current"]

        if current_state == "PAUSED":
            return "Service unavailable", 503
        elif current_state == "INIT":
            return "Service not initialized", 403
        elif current_state == "SHUTDOWN":
            return "Service has been shut down", 503

        # Proceed with fetching service info if the state is RUNNING
        # Fetch IP address
        ip_address = os.popen("hostname -I").read().strip()

        # Get list of running processes
        processes = [p.info for p in psutil.process_iter(['pid', 'name'])]

        # Get disk usage
        disk_usage = psutil.disk_usage('/')

        # Get system uptime
        uptime = os.popen("cat /proc/uptime").read().split()[0]

        # Build response
        response = {
            "Service": "Service1",
            "IP Address": ip_address,
            "Running Processes": processes,
            "Available Disk Space": disk_usage.free,
            "Uptime (seconds)": uptime
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8197, debug=True)
