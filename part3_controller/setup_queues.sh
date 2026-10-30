#!/bin/bash
# Run AFTER Mininet is started. Run from any folder: bash part3_controller/setup_queues.sh
# Queues go on the switch port facing HR (s1-eth4).
# Link is limited to 10 Mbps. Guaranteed minimums: INFO 2, WARNING/ERROR 3, CRITICAL 5 Mbps.
# Each queue may borrow unused bandwidth up to 10 Mbps, so INFO is never starved.

PORT=s1-eth4
RATE=10000000

sudo ovs-vsctl clear port $PORT qos 2>/dev/null
sudo ovs-vsctl --all destroy qos 2>/dev/null
sudo ovs-vsctl --all destroy queue 2>/dev/null

sudo ovs-vsctl -- set port $PORT qos=@newqos \
  -- --id=@newqos create qos type=linux-htb other-config:max-rate=$RATE \
       queues:1=@q1 queues:2=@q2 queues:3=@q3 \
  -- --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=$RATE \
  -- --id=@q2 create queue other-config:min-rate=3000000 other-config:max-rate=$RATE \
  -- --id=@q3 create queue other-config:min-rate=5000000 other-config:max-rate=$RATE

echo "Queues configured on $PORT:"
sudo ovs-vsctl list qos
sudo ovs-vsctl list queue
