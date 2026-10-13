import json
import subprocess
import sys
import time
import os

with open("config/project_config.json") as file:
    config = json.load(file)

DURATION = config["experiment"]["duration_seconds"]
NUM_CLIENTS = max(3, config["experiment"]["clients"])
RATE = config["experiment"]["logs_per_second_per_client"]
LEVELS = ["INFO", "WARNING", "CRITICAL", "ERROR"]

os.makedirs("results", exist_ok=True)
server_file = open("results/server_output.txt", "w")
server = subprocess.Popen(
    [sys.executable, "part1_app/server.py"],
    stdout=server_file,
    stderr=server_file
)
time.sleep(0.5)

clients = []
for i in range(NUM_CLIENTS):
    client_id = f"H{i + 1}"
    level = LEVELS[i % len(LEVELS)]
    process = subprocess.Popen(
        [sys.executable, "part1_app/client.py", client_id, level],
        stdout=subprocess.PIPE,
        text=True
    )
    clients.append(process)

sent = 0
client_results = []
for process in clients:
    output, _ = process.communicate()
    client_id, level, count = output.strip().split("|")
    count = int(count)
    sent += count
    client_results.append({"client_id": client_id, "level": level, "sent": count})
    print(f"{client_id}: level={level}, sent={count}")

server.wait()
server_file.close()

with open("results/server_output.txt") as file:
    server_output = file.read()

received = 0
receive_time = 0
throughput = 0
for line in server_output.splitlines():
    if line.startswith("SUMMARY|"):
        _, received, receive_time, throughput = line.split("|")
        received = int(received)
        receive_time = float(receive_time)
        throughput = float(throughput)

summary = {
    "duration_seconds": DURATION,
    "clients_started": NUM_CLIENTS,
    "logs_per_second_per_client": RATE,
    "sent": sent,
    "received": received,
    "estimated_loss": sent - received,
    "throughput_logs_per_second": throughput,
    "clients": client_results
}

with open("results/load_test_summary.json", "w") as file:
    json.dump(summary, file, indent=2)

print("\nLOAD TEST SUMMARY")
print(json.dumps(summary, indent=2))
print("\nReceiver details: results/server_output.txt")
