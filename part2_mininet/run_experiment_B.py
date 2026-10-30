
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
levels = ["INFO", "WARNING", "CRITICAL"]
hosts = ["H1", "H2", "H3"]

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
        with open(result_file, "w") as result:
            result.write("Experiment B - Competing UDP Traffic Without Priority\n")
            result.write(f"Date: {datetime.now().isoformat()}\n")
            result.write(f"Duration: {duration} seconds\n")
            result.write("H1: INFO, H2: WARNING, H3: CRITICAL\n")
            result.write("Configured rate: 20 logs/second/client\n\n")

            print("Starting Mininet topology...")
            from topology import LogAggregationTopo

            net = Mininet(
                topo=LogAggregationTopo(),
                controller=None,
                switch=OVSBridge
            )
            net.start()

            hr = net.get("HR")
            print("Starting UDP receiver...")

            server_output = open(server_log, "w")
            server = hr.popen(
                ["python3", "-u", str(PROJECT_DIR / "part1_app" / "server.py")],
                cwd=str(PROJECT_DIR),
                stdout=server_output,
                stderr=subprocess.STDOUT
            )

            time.sleep(2)

            if server.poll() is not None:
                raise RuntimeError("Receiver exited early. Check server log.")

            print("Starting three competing clients...")

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

            for host_name, level, process in clients:
                output, _ = process.communicate(timeout=duration + 15)
                result.write(f"{host_name} ({level}):\n{output}\n")

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

            result.write("\nReceiver output:\n")
            result.write(server_log.read_text(errors="replace"))
            result.write("\n")

        print("Experiment B finished.")
        print("Results:", result_file)
        print("Receiver log:", server_log)

    except Exception as error:
        print("Experiment B failed:", error)
        print("Check:", RESULT_DIR)
        raise

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
