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





def get_few_shot_prompt_for_solution(filtered_logs, critical_events, env, probe_note):
    pass

