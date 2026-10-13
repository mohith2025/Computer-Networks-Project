import json
import socket
import time

with open("config/project_config.json") as file:
    config = json.load(file)

SERVER_IP = config["server"]["host"]
SERVER_PORT = config["server"]["port"]
DURATION = config["experiment"]["duration_seconds"] + 2

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))
server.settimeout(0.2)

received = 0
first_log = None
last_log = None
start_time = time.time()
print(f"Server listening on {SERVER_IP}:{SERVER_PORT}", flush=True)

while time.time() - start_time < DURATION:
    try:
        data, address = server.recvfrom(4096)
    except socket.timeout:
        continue

    try:
        log = json.loads(data.decode())
        fields = ["client_id", "sequence", "level", "priority", "timestamp"]
        if not isinstance(log, dict) or not all(field in log for field in fields):
            continue
    except (ValueError, UnicodeDecodeError):
        continue

    now = time.time()
    if first_log is None:
        first_log = now
    last_log = now
    received += 1
    print(f"RECEIVED {log['client_id']} seq={log['sequence']} level={log['level']}", flush=True)

server.close()

if first_log is not None and last_log > first_log:
    receive_time = last_log - first_log
else:
    receive_time = 0

if receive_time > 0:
    throughput = received / receive_time
else:
    throughput = 0

print(f"SUMMARY|{received}|{receive_time:.3f}|{throughput:.2f}", flush=True)
