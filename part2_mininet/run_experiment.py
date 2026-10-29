
#!/usr/bin/env python3

import json
import time
import subprocess
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
server_ip = config["server"]["host"]
server_port = config["server"]["port"]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

result_file = RESULT_DIR / f"experiment_A_{timestamp}.txt"
server_log = RESULT_DIR / f"server_A_{timestamp}.log"

def main():
    net = None
    server = None
    client = None

    try:
        with open(result_file, "w") as result:
            result.write("Experiment A - Baseline UDP Delivery\n")
            result.write(f"Date: {datetime.now().isoformat()}\n")
            result.write(f"Duration: {duration} seconds\n")
            result.write(f"Receiver: {server_ip}:{server_port}\n")
            result.write("Traffic: H1 sends INFO logs\n\n")

            print("Starting Mininet topology...")
            from topology import LogAggregationTopo
            net = Mininet(
                topo=LogAggregationTopo(),
                controller=None,
                switch=OVSBridge
            )
            net.start()

            hr = net.get("HR")
            h1 = net.get("H1")

            print("Starting UDP receiver...")
            with open(server_log, "w") as server_output:
                server = hr.popen(
                    ["python3", "-u", str(PROJECT_DIR / "part1_app" / "server.py")],
                    cwd=str(PROJECT_DIR),
                    stdout=server_output,
                    stderr=subprocess.STDOUT
                )

                time.sleep(2)

                if server.poll() is not None:
                    raise RuntimeError(
                        "Receiver exited early. Check the server log: "
                        + str(server_log)
                    )

                print("Sending INFO traffic from H1...")
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

                client_output, _ = client.communicate(
                    timeout=duration + 15
                )
                result.write("Client output:\n")
                result.write(client_output + "\n")

                if client.returncode != 0:
                    raise RuntimeError("Client failed; see the experiment log.")

                print("Waiting for receiver summary...")
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.terminate()
                    server.wait(timeout=3)

            result.write("\nReceiver output:\n")
            result.write(server_log.read_text(errors="replace"))
            result.write("\n")

            print("Experiment A finished.")
            print("Results:", result_file)
            print("Receiver log:", server_log)

    except Exception as error:
        print("Experiment failed:", error)
        print("Check logs in:", RESULT_DIR)
        raise

    finally:
        if client is not None and client.poll() is None:
            client.terminate()
        if server is not None and server.poll() is None:
            server.terminate()
        if net is not None:
            net.stop()

if __name__ == "__main__":
    main()
