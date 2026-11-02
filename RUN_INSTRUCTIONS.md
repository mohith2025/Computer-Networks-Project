# Part 2 corrected — Mininet + Ryu only

## Experiment A (priority mode)
Start Ryu from project root:
```bash
cd ~/final_cn_project
source ~/cn-project/ryu-env/bin/activate
ryu-manager part3_controller/controller.py
```
Then separate terminal:
```bash
cd ~/final_cn_project
sudo python3 part2_mininet/run_experiment.py
```

## Experiment B (baseline mode)
Stop Ryu from A and launch baseline Ryu:
```bash
cd ~/final_cn_project
source ~/cn-project/ryu-env/bin/activate
MODE=baseline ryu-manager part3_controller/controller.py
```
Then:
```bash
cd ~/final_cn_project
sudo python3 part2_mininet/run_experiment_B.py
```

Runners connect switch to Ryu at 127.0.0.1:6653 and configure QoS on s1-eth4 before clients. Mininet clients use optional third argument `sdn` to select class ports 5001/5002/5003; Part 1 load_test omits it and continues to target configured server port. Queue minimums 2+3+5 Mbps = 10 Mbps matching the 10 Mbps bottleneck.

Python syntax checked. Runtime Mininet/Ryu end-to-end test not available here.
