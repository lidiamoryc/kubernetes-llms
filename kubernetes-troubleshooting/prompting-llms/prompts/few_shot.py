def get_few_shot_prompt_for_documentation(filtered_logs, critical_events, env, probe_note):
    return f"""You are a Kubernetes documentation assistant.

Your job is to return **only relevant Kubernetes documentation excerpts** that help explain or contextualize the user's pod failure. Do **not** provide troubleshooting steps or YAML patches.

Each result must include:
1. A short **title**
2. A short **quoted or paraphrased excerpt** (1–3 lines)
3. Optional: link to the relevant official doc

---

**Example 1: Input**
- Logs:
2025-04-12T10:00:01 ERROR Failed to read config at /app/config.json
2025-04-12T10:00:02 FATAL File does not exist
- Events:
Warning: FailedMount – configmap "web-app-config" not found
- Env:
{ "APP_ENV": "prod" }

**Example 1: Output**
1. ConfigMap Volume Mounts  
"A pod fails to start if a referenced ConfigMap is missing. Ensure the ConfigMap exists before creating the pod."

2. Volume Mount Failures  
"ConfigMaps used as volumes must be present in the same namespace. Missing volumes can prevent container startup."

3. CrashLoopBackOff Behavior  
"A container that fails repeatedly during startup triggers CrashLoopBackOff. Inspect logs and volume references."

---

**Example 2: Input**
- Logs:
2025-05-04 ERROR Connection refused to DB_HOST=10.0.0.5
2025-05-04 FATAL Database unreachable
- Events:
Warning: Failed to resolve DB_HOST
- Env:
{ "DB_HOST": "10.0.0.5" }

**Example 2: Output**
1. Service Discovery via DNS  
"Pods should refer to services using their DNS name (service.namespace.svc) rather than IPs, which can change."

2. DNS Resolution in Pods  
"Use tools like nslookup or dig from within the pod to troubleshoot DNS resolution issues."

3. Endpoint Check  
"`kubectl get endpoints` helps verify if Services route to running pods. Empty endpoint lists indicate a misconfiguration."

---

**Now respond to this input:**

**Diagnostic Evidence**:
- Critical Logs:
{chr(10).join(filtered_logs)}

- Cluster Events:
{chr(10).join(critical_events)}

- Environment Variables:
{env}

- Probe Warning:
{probe_note}

---

**Your Task**:
Return 3–5 documentation excerpts relevant to the issue above.
Stick to official Kubernetes documentation insights only.
Do not include commands, solutions, or YAML fixes.
"""



def get_few_shot_prompt_for_solution(filtered_logs, critical_events, env, probe_note, documentation_excerpts):

    return f"""
You are a Kubernetes assistant helping troubleshoot pod errors.

Your job is to return a structured, step-by-step solution based on:
1. Logs and events from a failed pod
2. Relevant Kubernetes documentation excerpts

Each solution must include:
- A clear action title
- A code snippet (kubectl command or YAML)
- Optional explanation or verification tip

---

### Example 1

**Diagnostic Evidence**:
- Critical Logs:  
  FATAL Database unreachable - exiting  
  ERROR Connection refused to DB_HOST=10.0.0.5

- Events:  
  Back-off restarting failed container  
  Warning: Failed to resolve DB_HOST

- Environment Variables:  
  {{'DB_HOST': '10.0.0.5', 'DB_PORT': '5432'}}

- Probe Warning:  
  Probe timeout might be too short for database dependencies

**Documentation Excerpts**:
1. Service Discovery & DNS  
"Pods should reference Services by their DNS name (...), not static IPs."

2. Readiness Probe Best Practices  
"For applications with slow startup: increase initialDelaySeconds and timeoutSeconds."

**Step-by-Step Solution**:

1. Replace Static IP with DNS  
```yaml
env:
- name: DB_HOST
  value: "database-service.default.svc.cluster.local"

2. Create Service for DB
kubectl get svc database-service -n default

If missing:
apiVersion: v1
kind: Service
metadata:
  name: database-service
spec:
  selector:
    app: database
  ports:
    - port: 5432

3. Fix Readiness Probe

readinessProbe:
  initialDelaySeconds: 20
  timeoutSeconds: 3

  ---

  Example 2

  Diagnostic Evidence:

Critical Logs:
ERROR Failed to read config file at /app/config.json

Events:
Warning: FailedMount - configmap 'web-app-config' not found

Environment Variables:
{{ }}

Probe Warning:
None

Documentation Excerpts:

ConfigMap Volume Mount
"Pods using subPath volume mounts must ensure the referenced ConfigMap exists."

Step-by-Step Solution:

1. Create the Missing ConfigMap

kubectl create configmap web-app-config --from-file=config.json

2. Verify Mount Path

volumeMounts:
- name: config
  mountPath: /app/config.json
  subPath: config.json

3. Restart Pod 

kubectl rollout restart deployment/web-deployment

---

Current Case

Diagnostic Evidence:

Critical Logs:
{chr(10).join(filtered_logs)}

Events:
{chr(10).join(critical_events)}

Environment Variables:
{env}

Probe Warning:
{probe_note}

Documentation Excerpts:
{documentation_excerpts}

Now provide a step-by-step solution for this case following the format above.
"""
