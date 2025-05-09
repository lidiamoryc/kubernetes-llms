
def get_one_shot_prompt_for_documentation(filtered_logs, critical_events, env, probe_note):

    return f"""You are a Kubernetes documentation assistant.

Your task is to return **only relevant official documentation excerpts** based on the user's Kubernetes pod error. Do not suggest commands or troubleshooting steps.

---

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

**Instructions**:
Return 3 to 5 short excerpts **quoted or paraphrased from official Kubernetes documentation** that relate to the error symptoms, configuration, or control plane behavior.

Each entry must include:
1. A short, clear **title**
2. A **brief documentation quote** (1–3 lines)
3. Optional: a documentation link (if known)

---

**Example**:

1. Service Discovery & DNS  
"Pods should reference Services using DNS (e.g. my-service.default.svc.cluster.local) rather than hardcoded IPs. Static IPs can change unexpectedly."

2. CrashLoopBackOff Behavior  
"A pod enters CrashLoopBackOff when its containers repeatedly fail. Use `kubectl logs --previous` to examine the last failed attempt."

3. Readiness Probes  
"For applications with slow startup, increase `initialDelaySeconds`. Keep `timeoutSeconds` high enough to allow expected response times."

4. Endpoint Troubleshooting  
"`kubectl get endpoints` helps verify if Services route correctly. Empty endpoints suggest no Pods match the Service selector."

---

**Now generate documentation excerpts for this case.**
Only return documentation. Do not propose solutions, kubectl commands, or YAML.
"""



def get_one_shot_prompt_for_solution(filtered_logs, critical_events, env, probe_note, documentation_excerpts):
    return f"""You are a Kubernetes assistant helping troubleshoot pod errors.

Your task is to propose a **step-by-step solution** based on the provided Kubernetes error signals and the most relevant official documentation excerpts.

---

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

**Documentation Excerpts**:
{documentation_excerpts}

---

### Example Output

Step by step solution:

1. Replace Static IP with Service DNS Name  
```yaml
# Before
env: {{"DB_HOST": "10.0.0.5"}}

# After
env:
- name: DB_HOST
  value: "database-service.default.svc.cluster.local"

  2. Verify Database Service Exists

  kubectl get svc database-service -n default

  If missing, create the service:

    apiVersion: v1
    kind: Service
    metadata:
    name: database-service
    namespace: default
    spec:
    selector:
        app: database
    ports:
        - protocol: TCP
        port: 5432
        targetPort: 5432

  3. Check Service Endpoints

  kubectl get endpoints database-service -o wide

  4. Test DNS Resolution

  kubectl exec web-pod -- nslookup database-service.default.svc.cluster.local

  5. Validate Network Connectivity

  kubectl exec web-pod -- nc -zv database-service.default.svc.cluster.local 5432

  6. Adjust Readiness Probes

  readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 20
  timeoutSeconds: 3
  periodSeconds: 5

  7. Restart & Monitor

  kubectl rollout restart deployment/web-deployment
  kubectl get pods -w

  Now, based on the diagnostic data and documentation, generate a similarly structured step-by-step solution.

  """