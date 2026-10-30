#!/bin/bash
# Run from the project root while Mininet is up:
#   bash part3_controller/verify.sh NAME
# Saves flows, queue config and queue counters to part3_controller/evidence/NAME.txt

NAME=${1:-check}
mkdir -p part3_controller/evidence
OUT=part3_controller/evidence/$NAME.txt

{
  date
  echo "===== FLOWS ====="
  sudo ovs-ofctl -O OpenFlow13 dump-flows s1
  echo "===== QOS CONFIG ====="
  sudo ovs-vsctl list qos
  echo "===== QUEUE CONFIG ====="
  sudo ovs-vsctl list queue
  echo "===== QUEUE COUNTERS ====="
  sudo ovs-ofctl -O OpenFlow13 queue-stats s1
} | tee "$OUT"

echo "Saved to $OUT"
