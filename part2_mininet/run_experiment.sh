
#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if [ "$#" -ne 1 ]; then
    echo "Usage: bash part2_mininet/run_experiment.sh A|B"
    exit 1
fi

EXPERIMENT="$1"

case "$EXPERIMENT" in
    A)
        RUNNER="part2_mininet/run_experiment.py"
        ;;
    B)
        RUNNER="part2_mininet/run_experiment_B.py"
        ;;
    *)
        echo "Invalid experiment: $EXPERIMENT"
        echo "Available experiments: A, B"
        exit 1
        ;;
esac

if [ ! -f "$RUNNER" ]; then
    echo "Runner not found: $RUNNER"
    exit 1
fi

echo "======================================"
echo " Starting Experiment $EXPERIMENT"
echo "======================================"
echo "Project: $PROJECT_DIR"
echo "Date: $(date)"
echo

sudo python3 "$RUNNER"
