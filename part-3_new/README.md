# Part 3 — Ryu Controller and OVS QoS (aligned with Part 2)

## Classifier and controller mapping
The SDN client sends UDP packets to destination ports:
- INFO: 5001 -> queue 1
- WARNING / ERROR: 5002 -> queue 2
- CRITICAL: 5003 -> queue 3

The Ryu flow matches IPv4 UDP packets destined to HR (10.0.0.4), applies
`SetQueue`, rewrites UDP destination to the configured server port (normally
9999), and outputs on switch port 4 (s1-eth4).

`MODE=baseline` sends all three classes through queue 1. Default mode is
priority.

## Run
From project root, with config file in `config/project_config.json` (or
`project_config.json` / `config.json`):
```bash
source ~/cn-project/ryu-env/bin/activate
ryu-manager part3_controller/controller.py
```
Start Experiment A from another terminal:
```bash
sudo python3 part2_mininet/run_experiment.py
```
For Experiment B, stop Ryu then launch:
```bash
MODE=baseline ryu-manager part3_controller/controller.py
```
Then:
```bash
sudo python3 part2_mininet/run_experiment_B.py
```

The queue setup script should be run after Mininet has started:
```bash
bash part3_controller/setup_queues.sh
```
Part 2's fixed runners already invoke this script if it is located at
`part3_controller/setup_queues.sh`.

## Bandwidth
Queue minimums total 10 Mbps (2 + 3 + 5), matching the configured 10 Mbps
bottleneck. Each queue's maximum is 10 Mbps, allowing it to borrow unused
capacity. If actual bottleneck bandwidth is set below 10 Mbps, these minimum
rates must be lowered so their sum does not exceed that capacity.

## Important
Python syntax was checked. This bundle has not been tested end-to-end on your
Mininet/OVS/Ryu VM; verify Ryu switch connection and `ovs-ofctl -O OpenFlow13
dump-flows s1` before collecting experiment results.
