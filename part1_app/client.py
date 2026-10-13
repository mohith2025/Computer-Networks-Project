import json
import socket
import time
import sys
from datetime import datetime, timezone

with open("config/project_config.json") as file:
    config = json.load(file)

SERVER_IP = config["server"]["host"]
SERVER_PORT = config["server"]["port"]
DURATION = config["experiment"]["duration_seconds"]
RATE = config["experiment"]["logs_per_second_per_client"]

client_id = sys.argv[1]
level = sys.argv[2]
priority = config["log_levels"][level]["priority"]

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sent = 0
start_time = time.time()

while time.time() - start_time < DURATION:
    log = {
        "client_id": client_id,
        "sequence": sent + 1,
        "level": level,
        "priority": priority,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    client.sendto(
        json.dumps(log).encode(),
        (SERVER_IP, SERVER_PORT)
    )
    sent += 1
    time.sleep(1 / RATE)

client.close()
print(f"{client_id}|{level}|{sent}")
