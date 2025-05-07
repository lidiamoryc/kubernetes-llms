
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
