
#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESULT_DIR="$PROJECT_DIR/results/part2"
CONFIG="$PROJECT_DIR/config/project_config.json"

if [ "$#" -ne 1 ]; then
    echo "Usage: bash part2_mininet/run_experiment.sh A"
    exit 1
fi

EXPERIMENT="$1"

if [ "$EXPERIMENT" != "A" ]; then
    echo "Only Experiment A is implemented in this version."
    echo "B, C and D will be added after A is verified."
    exit 1
fi

mkdir -p "$RESULT_DIR"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$RESULT_DIR/experiment_A_${TIMESTAMP}.txt"

{
    echo "Experiment: A - Baseline UDP delivery"
    echo "Date: $(date)"
    echo "Project: $PROJECT_DIR"
    echo
    echo "Configuration:"
    cat "$CONFIG"
    echo
    echo "Topology: H1, H2, H3, HR connected to s1"
    echo "Receiver: 10.0.0.4:9999"
    echo
    echo "This script records experiment metadata only."
    echo "Run the Mininet receiver and client commands separately."
    echo "Do not treat this file as measured experiment results."
} | tee "$LOG"

echo
echo "Metadata saved to: $LOG"
