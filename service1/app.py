from flask import Flask, request, jsonify
import logging
import datetime
import os
import psutil
import subprocess

app = Flask(__name__)

# State management
state = {"current": "INIT"}
state_log = []

# Logger setup
logging.basicConfig(filename='state_changes.log', level=logging.INFO, format='%(asctime)s: %(message)s')

def log_state_change(prev, new):
    """
    Logs the transition from one state to another in both the application state log and the log file.
    :param prev: Previous state.
    :param new: New state.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp}: {prev}->{new}"
    state_log.append(log_entry)
    logging.info(log_entry)

def stop_all_containers():
    """
    Stops all running Docker containers on the system.
    Logs any errors encountered during the process.
    """
    try:
        # List all running containers
        running_containers = subprocess.check_output(
            ["docker", "ps", "-q"], text=True
        ).strip().splitlines()

        if not running_containers:
            logging.info("No running containers to stop.")
            return

        # Stop each container
        for container_id in running_containers:
            subprocess.check_call(["docker", "stop", container_id])
            logging.info(f"Stopped container: {container_id}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error stopping containers: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

@app.route('/state', methods=['PUT'])
def update_state():
    """
    Updates the current application state based on the request payload.
    Accepts "text/plain" or "application/json" content types.
    Handles special cases like INIT and SHUTDOWN states.
    """
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
        stop_all_containers()  # Stop all running containers

    return f"State changed to {new_state}", 200

@app.route('/state', methods=['GET'])
def get_state():
    """
    Retrieves the current state of the application.
    """
    return state["current"], 200

@app.route('/request', methods=['GET'])
def request_service():
    """
    Simulates a service request.
    Returns a 503 Service Unavailable response if the application state is PAUSED.
    """
    if state["current"] == "PAUSED":
        return "Service unavailable", 503
    return "Service response: OK", 200

@app.route('/run-log', methods=['GET'])
def get_run_log():
    """
    Returns a log of all state changes in the application.
    """
    return "\n".join(state_log), 200

@app.route('/api', methods=['GET'])
def get_service_info():
    """
    Fetches system and service-related information such as IP address, running processes,
    disk space, and uptime. Availability depends on the application state.
    """
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
    # Run the Flask app on port 8197, accessible from any network interface
    app.run(host="0.0.0.0", port=8197, debug=True)
