
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



def get_one_shot_prompt_for_solution(filtered_logs, critical_events, env, probe_note):
    pass
