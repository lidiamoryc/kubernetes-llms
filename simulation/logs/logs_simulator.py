import time
import random
from datetime import datetime

# example logs for simulation
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

def generate_log_entry():
    timestamp = datetime.utcnow().isoformat() + "Z"
    level = random.choices(log_levels, weights=[0.6, 0.25, 0.15])[0]
    component = random.choice(components)
    message = random.choice(messages[level])
    return f"{timestamp} {level} {component}: {message}"

def main():
    logfile = open("k8s_fake_logs.log", "a")

    try:
        while True:
            log = generate_log_entry()
            print(log)
            logfile.write(log + "\n")
            logfile.flush()
            time.sleep(random.uniform(0.5, 1.5))  

    except KeyboardInterrupt:
        print("\nLog generation stopped.")
        logfile.close()

if __name__ == "__main__":
    main()

