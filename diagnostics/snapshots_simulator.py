import time
import random
import json
from datetime import datetime
import os

# example logs data sources
components = ["kubelet", "scheduler", "controller-manager", "etcd", "apiserver"]
log_levels = ["INFO", "WARNING", "ERROR"]
messages = {
    "INFO": [
        "Started container successfully",
        "Successfully pulled image 'nginx:latest'",
        "Node registered with the cluster"
    ],
    "WARNING": [
        "CPU pressure detected on node",
        "Pod eviction triggered due to memory usage",
        "Container took too long to start"
    ],
    "ERROR": [
        "Failed to start container runtime",
        "Image pull failed: connection timeout",
        "Pod crashloop backoff"
    ]
}
pods = ["api-server-pod", "nginx-deployment-xyz", "redis-cache-abc"]
nodes = ["node-1", "node-2"]

output_file = "k8s_fake_snapshots.json"

# simulation
def generate_snapshot():
    timestamp = datetime.utcnow().isoformat() + "Z"

    pods_list = [
        f"{pod},1/1,Running,{random.randint(0,3)},{random.randint(1,120)}m,10.1.{random.randint(1,4)}.{random.randint(10,250)},{random.choice(nodes)}"
        for pod in pods
    ]

    describe = f"""Name: api-server-pod
Namespace: default
Node: node-1
Status: Running
IP: 10.1.2.34
Restart Count: {random.randint(0, 5)}
Events:
  Type     Reason     Age   From     Message
  ----     ------     ---   ----     -------
  Normal   Pulled     1m    kubelet  Container image pulled
  Warning  BackOff    2m    kubelet  Back-off restarting failed container
"""

    logs = "\n".join([
        f"[{lvl}] {random.choice(messages[lvl])}" for lvl in log_levels for _ in range(random.randint(1, 2))
    ])

    events = """LAST SEEN   TYPE      REASON     OBJECT             MESSAGE
1m          Warning   BackOff    pod/api-server     Back-off restarting failed container
2m          Normal    Pulled     pod/api-server     Successfully pulled image "api:v1.2"
"""

    top_pods = """NAMESPACE     NAME              CPU(cores)   MEMORY(bytes)
default       api-server-pod    120m         890Mi
default       redis-cache        30m         110Mi
"""

    node_desc = f"""Name: node-1
MemoryPressure: False
DiskPressure: False
Conditions:
  Ready: True
  MemoryPressure: False
Taints: <none>
"""

    return {
        "timestamp": timestamp,
        "pods": pods_list,
        "describe": describe,
        "logs": logs,
        "events": events,
        "top_pods": top_pods,
        "node": node_desc
    }

def load_existing_snapshots():
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_snapshots(data):
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

def main():
    print("Fake Kubernetes snapshot simulator running...")
    print("Saving to:", output_file)
    print("Interval: 30 seconds. Press Ctrl+C to stop.\n")

    snapshots = load_existing_snapshots()

    try:
        while True:
            snapshot = generate_snapshot()
            snapshots.append(snapshot)
            save_snapshots(snapshots)
            print(f"Snapshot saved at {snapshot['timestamp']}")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

if __name__ == "__main__":
    main()
