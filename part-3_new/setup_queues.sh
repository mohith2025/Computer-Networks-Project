#!/bin/bash
set -e

# Run after Mininet starts. QoS is applied only to the switch port connected
# to HR (s1-eth4), the project's 10 Mbps bottleneck.
PORT="s1-eth4"
RATE=10000000

if ! sudo ovs-vsctl --if-exists get Port "$PORT" name >/dev/null 2>&1; then
  echo "ERROR: OVS port $PORT does not exist. Start Mininet first."
  exit 1
fi

# Detach any QoS currently attached to this specific port.
sudo ovs-vsctl --if-exists clear Port "$PORT" qos

# Build QoS + three queues in one transaction. Guaranteed minimums add to
# 10 Mbps: INFO=2, WARNING/ERROR=3, CRITICAL=5. Max is 10 Mbps each.
sudo ovs-vsctl -- set Port "$PORT" qos=@qos \
  -- --id=@qos create QoS type=linux-htb other-config:max-rate="$RATE" \
       queues:1=@q1 queues:2=@q2 queues:3=@q3 \
  -- --id=@q1 create Queue other-config:min-rate=2000000 other-config:max-rate="$RATE" \
  -- --id=@q2 create Queue other-config:min-rate=3000000 other-config:max-rate="$RATE" \
  -- --id=@q3 create Queue other-config:min-rate=5000000 other-config:max-rate="$RATE"

echo "QoS configured on $PORT"
sudo ovs-vsctl list QoS
sudo ovs-vsctl list Queue
