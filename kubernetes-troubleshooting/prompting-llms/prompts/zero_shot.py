
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


def get_zero_shot_prompt_for_solution(filtered_logs, critical_events, env, probe_note):

    pass
## to improve


    # return f"""Troubleshoot this Kubernetes CrashLoopBackOff error:

    #             **Diagnostic Evidence**:
    #             - Critical Logs: {chr(10).join(self.filtered_logs)}
    #             - Cluster Events: {chr(10).join(self.critical_events)}
    #             - Database Config: {json.dumps(self.data.get('env', {}), indent=2)}
    #             - Probe Warning: {self.probe_note}

    #             **Required Response Format**:
    #             Relevant Documentation Excerpts:

    #             List 3-5 Kubernetes documentation snippets. For each, include:
    #             1. A short **title**
    #             2. A brief **quoted excerpt** from Kubernetes docs (1-2 lines)

    #             Format:
    #             1. <Title>  
    #             "<documentation quote>"

    #             ...

    #             Step by step solution:

    #             Provide a **numbered list of actions**. Each step should include:
    #             - A short **title**
    #             - **Code snippet**, **kubectl command**, or YAML config fix
    #             - Optional reasoning or verification tip

    #             Format:
    #             1. <Step Name>  
    #             <command, YAML or explanation>

    #             ...

    #             Ensure the answer is **structured, actionable, and faithful to Kubernetes best practices**.
    #             """

