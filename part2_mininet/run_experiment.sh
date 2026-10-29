
#!/bin/bash
set -u

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESULT_DIR="$PROJECT_DIR/results/part2"

mkdir -p "$RESULT_DIR"

if [ "$#" -lt 1 ]; then
    echo "Usage: bash part2_mininet/run_experiment.sh A"
    echo "Experiments: A, B, C, D"
    exit 1
fi

EXPERIMENT="$1"

case "$EXPERIMENT" in
    A|B|C|D) ;;
    *)
        echo "Invalid experiment. Choose A, B, C, or D."
        exit 1
        ;;
esac

echo "Experiment $EXPERIMENT selected."
echo "Project: $PROJECT_DIR"
echo "Results: $RESULT_DIR"

echo
echo "This script currently prepares the experiment folder."
echo "It does not yet run the Mininet traffic or enable priority queues."
echo "Those steps will be added after we confirm the controller and queue setup."
