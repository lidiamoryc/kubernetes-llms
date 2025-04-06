# 🧪 Observing a Deployed App in Kubernetes: Logs & Crash Reasons

This note summarizes all the possible ways to extract information from a deployed application in Kubernetes, including where to find **crash/error reasons** — both from **inside the app** and from **Kubernetes itself**.

---

## 📍 Ways to Access Runtime Information

### 1. **App Logs (stdout/stderr)**
- Command:
  ```bash
  kubectl logs <pod-name>
  kubectl logs <pod-name> --previous  # For crashed pods
  ```

  - This contains:
    - Console logs (print, console.log, logger output)
    - Stack traces
    - Custom timestamps, log levels (if implemented)

### 2. **Pod Description**
- Command:
  ```bash
  kubectl describe pod <pod-name>
  ```

- This contains:
    - Crash reasons, restart count
    - Container states and exit codes
    - Recent events (e.g., OOMKilled, BackOff)

### 3. **Events (Cluster-Wide or Namespace)**
- Command:
  ```bash
  kubectl get events --sort-by=.metadata.creationTimestamp
  ```

- This contains:
  - Scheduling issues
  - Container/image errors
  - Pod evictions, restarts
 
### 4. **Pod details**
- Commands:
  ```bash
  kubectl get pod <pod-name> -o wide
  kubectl get pod <pod-name> -o yaml
  kubectl get pod <pod-name> -o json
  ```

- This contains:
  - Node name, IPs, labels
  - Resource requests/limits
  - Volume mounts, env vars
 
### 5. **Node Inspection**

- Command:
  ```bash
  kubectl describe node <node-name>
  ```

- This contains:
  - Resource pressure (memory, disk)
  - Allocatable/used resources
  - Node-level issues affecting pods

### 6. **Inside the Pod**

- Command:
  ```bash
  kubectl exec -it <pod-name> -- bash
  printenv           # Show environment variables
  cat /app/logs/...  # If app logs to file
  ```

### 7. **Job / CronJob Info**

- Command:
  ```bash
  kubectl get jobs
  kubectl describe job <job-name>
  kubectl logs job/<job-name>
  ```

For checking scheduled tasks like time-based bots.

---

## ⚠️ Two Sources of Crash Reasons

1. App-Level Errors (Handled in Code)
Found in: kubectl logs

Examples:
- Exceptions (e.g., Python KeyError, Node TypeError)
- Failed Discord API calls
- Invalid config or missing tokens
- Scheduler logic issues

| Type             | Source                 | Example                     |
|------------------|------------------------|-----------------------------|
| Basic Messages   | `print()`              | `"Bot started"`            |
| Error Messages   | `print(e)`, unhandled exception | `"KeyError: 'token'"` |
| Structured Logs  | `logging` module       | `"[INFO] Bot ready"`       |
| JSON Logs        | `json.dumps(...)`      | `{"event": "started"}`     |
| Debug Info       | Manual `print()`       | `"response code: 403"`     |
| Warnings         | `warnings.warn()`      | `"Deprecated usage"`       |
| Library Logs     | `discord.py`, etc.     | `"[WARNING] Rate limit"`   |
| Fatal Crashes    | Python itself          | Stack trace or `SyntaxError` |

 
2. Kubernetes-Level Errors (System-Induced)
Found in: kubectl describe pod, kubectl get events

Examples:
- OOMKilled (Out of memory)
- CrashLoopBackOff (Repeated crashes)
- ImagePullBackOff (Image not found)
- Evicted (Node ran out of resources)
- Exit Code 1/137 (General crash or signal kill)

