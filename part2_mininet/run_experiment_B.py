
#!/usr/bin/env python3

import json
import time
import subprocess
import re
from pathlib import Path
from datetime import datetime

from mininet.net import Mininet
from mininet.node import OVSBridge

PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = PROJECT_DIR / "results" / "part2"
CONFIG_FILE = PROJECT_DIR / "config" / "project_config.json"

with open(CONFIG_FILE) as f:
    config = json.load(f)

duration = config["experiment"]["duration_seconds"]
rate = config["experiment"]["logs_per_second_per_client"]

hosts = ["H1", "H2", "H3"]
levels = ["INFO", "WARNING", "CRITICAL"]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

result_file = RESULT_DIR / f"experiment_B_{timestamp}.txt"
server_log = RESULT_DIR / f"server_B_{timestamp}.log"


def main():
    net = None
    server = None
    clients = []
    server_output = None

    try:
        print("Starting Mininet topology...")
        from topology import LogAggregationTopo

        net = Mininet(
            topo=LogAggregationTopo(),
            controller=None,
            switch=OVSBridge
        )
        net.start()

        hr = net.get("HR")
        server_output = open(server_log, "w")

        print("Starting UDP receiver...")
        server = hr.popen(
            ["python3", "-u", str(PROJECT_DIR / "part1_app" / "server.py")],
            cwd=str(PROJECT_DIR),
            stdout=server_output,
            stderr=subprocess.STDOUT
        )

        time.sleep(2)

        if server.poll() is not None:
            raise RuntimeError("Receiver exited early. Check server log.")

        print("Starting three clients...")
        for host_name, level in zip(hosts, levels):
            host = net.get(host_name)
            process = host.popen(
                [
                    "python3", "-u",
                    str(PROJECT_DIR / "part1_app" / "client.py"),
                    host_name, level
                ],
                cwd=str(PROJECT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            clients.append((host_name, level, process))

        client_results = []

        for host_name, level, process in clients:
            output, _ = process.communicate(timeout=duration + 15)
            match = re.search(r"\|(\w+)\|(\d+)", output)

            if not match:
                raise RuntimeError(
                    f"Could not read sent count from {host_name}. Output: {output}"
                )

            sent = int(match.group(2))
            client_results.append((host_name, level, sent))

            print(f"{host_name} ({level}) sent: {sent}")

            if process.returncode != 0:
                raise RuntimeError(f"{host_name} client failed.")

        print("Waiting for receiver summary...")
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.terminate()
            server.wait(timeout=3)

        server_output.close()
        server_output = None

        receiver_text = server_log.read_text(errors="replace")
        summary_match = re.search(
            r"SUMMARY\|(\d+)\|([\d.]+)\|([\d.]+)",
            receiver_text
        )

        if not summary_match:
            raise RuntimeError(
                "Receiver summary missing. Check: " + str(server_log)
            )

        received = int(summary_match.group(1))
        interval = float(summary_match.group(2))
        throughput = float(summary_match.group(3))

        total_sent = sum(item[2] for item in client_results)
        lost = total_sent - received
        loss_percent = (lost / total_sent * 100) if total_sent else 0

        with open(result_file, "w") as result:
            result.write("Experiment B - Competing UDP Traffic Without Priority\n")
            result.write(f"Date: {datetime.now().isoformat()}\n")
            result.write(f"Duration: {duration} seconds\n")
            result.write(f"Configured rate per client: {rate} logs/sec\n\n")

            for host_name, level, sent in client_results:
                result.write(f"{host_name} ({level}) sent: {sent}\n")

            result.write(f"\nTotal sent: {total_sent}\n")
            result.write(f"Total received: {received}\n")
            result.write(f"Estimated lost: {lost}\n")
            result.write(f"Estimated loss percentage: {loss_percent:.2f}%\n")
            result.write(f"Measurement interval: {interval:.3f} seconds\n")
            result.write(f"Throughput: {throughput:.2f} logs/sec\n")

            if lost < 0:
                result.write("WARNING: Received count exceeds sent count; investigate.\n")

        print("\nExperiment B finished.")
        print("Total sent:", total_sent)
        print("Total received:", received)
        print("Estimated loss:", lost)
        print(f"Estimated loss percentage: {loss_percent:.2f}%")
        print(f"Throughput: {throughput:.2f} logs/sec")
        print("Results:", result_file)
        print("Receiver log:", server_log)

    finally:
        for _, _, process in clients:
            if process.poll() is None:
                process.terminate()

        if server is not None and server.poll() is None:
            server.terminate()

        if server_output is not None:
            server_output.close()

        if net is not None:
            net.stop()


if __name__ == "__main__":
    main()
