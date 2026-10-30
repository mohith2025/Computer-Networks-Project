
#!/usr/bin/env python3

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.link import TCLink


PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = PROJECT_DIR / "results" / "part2"
CONFIG_FILE = PROJECT_DIR / "config" / "project_config.json"

with open(CONFIG_FILE) as f:
    config = json.load(f)

duration = config["experiment"]["duration_seconds"]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

result_file = RESULT_DIR / f"experiment_A_{timestamp}.txt"
server_log = RESULT_DIR / f"server_A_{timestamp}.log"


def main():
    net = None
    server = None
    client = None
    server_output = None

    try:
        print("Starting Mininet topology...")

        from topology import LogAggregationTopo

        net = Mininet(
            topo=LogAggregationTopo(),
            controller=None,
            switch=OVSBridge,
            link=TCLink
        )

        net.start()

        hr = net.get("HR")
        h1 = net.get("H1")

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

        print("Starting H1 INFO client...")

        client = h1.popen(
            [
                "python3", "-u",
                str(PROJECT_DIR / "part1_app" / "client.py"),
                "H1", "INFO"
            ],
            cwd=str(PROJECT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        client_output, _ = client.communicate(timeout=duration + 15)

        if client.returncode != 0:
            raise RuntimeError(f"Client failed. Output: {client_output}")

        print("Client output:")
        print(client_output.strip())

        print("Waiting for receiver summary...")

        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.terminate()
            server.wait(timeout=3)

        server_output.close()
        server_output = None

        receiver_text = server_log.read_text(errors="replace")

        import re

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

        result_text = (
            "Experiment A - Baseline Connectivity and Log Delivery\n"
            f"Date: {datetime.now().isoformat()}\n"
            f"Duration: {duration} seconds\n"
            "Client: H1 (INFO)\n"
            "Link bandwidth: 10 Mbps per host-to-switch link\n\n"
            f"Receiver total: {received}\n"
            f"Measurement interval: {interval:.3f} seconds\n"
            f"Throughput: {throughput:.2f} logs/sec\n"
        )

        result_file.write_text(result_text)

        print("\nExperiment A finished.")
        print(result_text)
        print("Results:", result_file)
        print("Receiver log:", server_log)

    finally:
        if client is not None and client.poll() is None:
            client.terminate()

        if server is not None and server.poll() is None:
            server.terminate()

        if server_output is not None:
            server_output.close()

        if net is not None:
            net.stop()


if __name__ == "__main__":
    main()
