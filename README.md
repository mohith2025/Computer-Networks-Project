# CN Project — Person 1 (Simple Code Style)

## Files
- `part1_app/client.py` — sends UDP JSON logs.
- `part1_app/server.py` — receives logs, prints client IDs and levels, and calculates throughput.
- `part1_app/load_test.py` — starts the server and at least three client processes, then saves a test summary.
- `config/project_config.json` — shared server, priority, queue, duration and switch settings.
- `results/` — saved test output and summary.

## Run on macOS
Run from this folder:

```bash
python3 part1_app/load_test.py
```

By default, three clients run for five seconds. Change the values in `config/project_config.json` to adjust duration, clients, or per-client sending rate.

## Outputs
- `results/load_test_summary.json`: sent/received counts, estimated loss, throughput and client details.
- `results/server_output.txt`: each valid log shown by the receiver and the final server summary.

## Required JSON fields
`client_id`, `sequence`, `level`, `priority`, and `timestamp`. The timestamp is UTC. JSON is used for each log message; the small `client_id|level|sent` line is only a simple way for the client process to report its count to `load_test.py`.

## Simple coding style
The scripts use constants, direct socket calls, loops, and straightforward print statements. No classes, `argparse`, `pathlib`, signal handlers, ACK protocol, or third-party packages are needed for this local baseline.

UDP is best-effort, so `estimated_loss` is only an estimate. The local baseline does not implement SDN queueing; that is Person 3's work, using Person 2's Mininet topology.
