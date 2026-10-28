
import json
import socket
import time

with open("config/project_config.json") as file:
    config = json.load(file)

SERVER_IP = config["server"]["host"]
SERVER_PORT = config["server"]["port"]
DURATION = config["experiment"]["duration_seconds"] + 2

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER_IP, SERVER_PORT))
server.settimeout(0.2)

received = 0
invalid = 0
first_log = None
last_log = None
start_time = time.time()

print(f"Server listening on {SERVER_IP}:{SERVER_PORT}", flush=True)

while time.time() - start_time < DURATION:
    try:
        data, address = server.recvfrom(4096)
    except socket.timeout:
        continue
    except OSError as error:
        print(f"SOCKET ERROR: {error}", flush=True)
        break

    print(f"PACKET FROM {address}, bytes={len(data)}", flush=True)

    try:
        log = json.loads(data.decode())
        fields = ["client_id", "sequence", "level", "priority", "timestamp"]

        if not isinstance(log, dict):
            invalid += 1
            print("INVALID: JSON is not an object", flush=True)
            continue

        missing = [field for field in fields if field not in log]
        if missing:
            invalid += 1
            print(f"INVALID: missing fields {missing}", flush=True)
            continue

    except (ValueError, UnicodeDecodeError) as error:
        invalid += 1
        print(f"INVALID PACKET: {error}; data={data!r}", flush=True)
        continue

    now = time.time()
    if first_log is None:
        first_log = now
    last_log = now
    received += 1

    print(
        f"RECEIVED {log['client_id']} "
        f"seq={log['sequence']} level={log['level']}",
        flush=True
    )

server.close()

receive_time = last_log - first_log if first_log is not None and last_log > first_log else 0
throughput = received / receive_time if receive_time > 0 else 0

print(f"INVALID PACKETS: {invalid}", flush=True)
print(f"SUMMARY|{received}|{receive_time:.3f}|{throughput:.2f}", flush=True)
