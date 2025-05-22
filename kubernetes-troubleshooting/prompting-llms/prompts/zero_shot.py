
def get_zero_shot_prompt_for_documentation(filtered_logs, critical_events, env, probe_note):

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
                        Return 3 to 5 short excerpts **quoted from official Kubernetes documentation** that relate to the error, configuration issues, or failure modes described above.

                        Each entry must include:
                        1. A short, clear **title**
                        2. A **direct quote or paraphrase** from Kubernetes documentation (1-3 lines max)
                        3. Optional: link to the section (if you know the official URL)

                        ---

                        **Response Format**:
                        1. <Title>  
                        "<relevant quote or paraphrased doc excerpt>"  
                        [Optional link]

                        2. ...

                        Only return documentation. Do not propose solutions, commands, or YAML configs.
                        """

def get_zero_shot_prompt_for_solution(filtered_logs, critical_events, env, probe_note, documentation_excerpts):

    return f"""You are a Kubernetes troubleshooting assistant.

The user previously retrieved **relevant Kubernetes documentation excerpts** to help explain a pod failure. Your task is to use this information, along with the observed logs and events, to generate a **step-by-step fix**.

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

**Relevant Documentation**:
{documentation_excerpts}

---

**Instructions**:
1. Use the documentation excerpts to infer the root cause.
2. Return a **brief root cause explanation** (1–2 sentences).
3. List **clear troubleshooting steps**, each with:
   - A short title
   - YAML fix or kubectl command
   - Optional: validation command or reasoning

---

**Response Format**:

**Root Cause**:  
<short explanation>

**Steps to Resolve**:

1. <Step Title>  
<code/config>  
<optional tip or explanation>

...
"""

def get_zero_shot_prompt_for_error_explanation(filtered_logs, critical_events, env, probe_note, documentation_excerpts):
    
    example_format = '''1. Replace Static IP with Service DNS Name

# Before
env: {"DB_HOST": "10.0.0.5"}

# After
env:
- name: DB_HOST
  value: "database-service.default.svc.cluster.local"  # Service DNS format

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
    app: database  # Must match database pod labels
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432'''
    
    prompt = f"""You are a Kubernetes troubleshooting expert.

You have been provided with Kubernetes error logs and relevant documentation excerpts. Your task is to provide a comprehensive solution to fix the Kubernetes issue.

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

**Relevant Documentation Excerpts**:
{documentation_excerpts}

---

**Instructions**:
1. Analyze the error logs and identify the root cause of the problem.
2. Start with a very brief root cause explanation (1-2 sentences maximum).
3. Then provide a detailed, step-by-step solution with numbered steps.
4. For each step:
   - Include a clear title
   - Show "Before" and "After" configurations when appropriate
   - Include kubectl commands where helpful
   - Provide brief explanations of what to look for in command output
   - Explain briefly what each step accomplishes

---

**Response Format**:
Start with a very brief root cause statement (no header, just 1-2 sentences), then immediately proceed to numbered steps as follows:

{example_format}

... (additional steps)

DO NOT include headers like "Error Analysis", "Root Cause" or "Implementation Steps". Start directly with the 1-2 sentence root cause explanation followed by numbered steps.
"""
    return prompt
