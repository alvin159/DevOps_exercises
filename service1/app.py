from flask import Flask, jsonify
import os
import psutil
import socket
import time

app = Flask(__name__)

@app.route('/')
def index():
    ip_address = socket.gethostbyname(socket.gethostname())
    processes = [p.info for p in psutil.process_iter(attrs=['pid', 'name'])]
    disk_usage = psutil.disk_usage('/')
    uptime = time.time() - psutil.boot_time()
    
    return jsonify({
        "Service": "Service1",
        "IP Address": ip_address,
        "Running Processes": processes,
        "Available Disk Space": disk_usage.free,
        "Uptime (seconds)": uptime
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)
