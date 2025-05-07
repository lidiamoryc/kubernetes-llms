import json
import os
import json
import os

from prompts.zero_shot import get_zero_shot_prompt_for_solution, get_zero_shot_prompt_for_documentation
from prompts.one_shot import get_one_shot_prompt_for_solution, get_one_shot_prompt_for_documentation
from prompts.few_shot import get_few_shot_prompt_for_solution, get_few_shot_prompt_for_documentation


class KubernetesPromptBuilder:
    def __init__(self, json_path: str):
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"File not found: {json_path}")
        
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        
        self._preprocess()


    def _preprocess(self):
        logs = self.data.get("logs", "")
        self.filtered_logs = [
            line.split(" ", 3)[-1]
            for line in logs.split("\n")
            if "ERROR" in line or "FATAL" in line
        ]

        self.critical_events = []
        for event in self.data.get("events", []):
            if any(k in event for k in ["Failed", "Back-off", "Warning"]):
                parts = event.split(": ", 1)
                self.critical_events.append(parts[1] if len(parts) > 1 else parts[0])

        self.probe_note = ""
        if self.data.get("probe_config", {}).get("timeoutSeconds", 1) < 2:
            self.probe_note = "Probe timeout might be too short for database dependencies"
        

    def build_prompt_for_documentation(self, mode="zero-shot") -> str:

        if mode == "zero-shot":

            return get_zero_shot_prompt_for_documentation(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)
        
        if mode == "one-shot":

            return get_one_shot_prompt_for_documentation(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)

        if mode == "few-shot":
    
            return get_few_shot_prompt_for_documentation(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)
        
        else:
            raise ValueError("Invalid mode. Choose 'zero-shot', 'one-shot', or 'few-shot'")
        


    def build_prompt_for_solution(self, mode="zero-shot") -> str:

        if mode == "zero-shot":
            
            pass

            # return get_zero_shot_prompt_for_solution(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)
        
            #TODO: think if we should parse it through the Pydantic for structured output?
            #TODO: is the ground truth in the correct format? we can adjust it

        elif mode == "one-shot":

            one_shot_example = """Relevant Documentation Excerpts:

                                1. Service Discovery & DNS
                                "Pods should reference Services by their DNS name (<service>.<namespace>.svc.cluster.local), not static IPs. IPs are ephemeral in Kubernetes clusters."

                                2. CrashLoopBackOff Definition
                                "A pod enters CrashLoopBackOff state when its containers repeatedly crash. Check logs with kubectl logs --previous to identify the root cause."

                                3. Readiness Probe Best Practices
                                "For applications with slow startup: set initialDelaySeconds longer than initialization time; timeoutSeconds should exceed request time."

                                4. Endpoint Verification
                                "Validate service-to-pod mapping with: kubectl get endpoints <service-name>. Empty results indicate no healthy pods match selectors."

                                5. DNS Resolution Troubleshooting
                                "Debug DNS issues using: kubectl exec -it <pod> -- nslookup <service>. Failures suggest CoreDNS issues or missing services."

                                Step by step solution:

                                1. Replace Static IP with Service DNS Name

                                # Before
                                env: { "DB_HOST": "10.0.0.5" }

                                # After
                                env:
                                - name: DB_HOST
                                value: "database-service.default.svc.cluster.local"

                                2. Verify Database Service Exists

                                kubectl get svc database-service -n default

                                If not found, define the service:

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

                                If empty: check pod labels or deployment.

                                4. Test DNS Resolution

                                kubectl exec web-pod -- nslookup database-service.default.svc.cluster.local

                                If fails: CoreDNS may be misconfigured.

                                5. Validate Network Connectivity

                                kubectl exec web-pod -- nc -zv database-service.default.svc.cluster.local 5432

                                If timeout: check firewall rules and pod readiness.

                                6. Adjust Readiness Probe

                                readinessProbe:
                                httpGet:
                                    path: /health
                                    port: 8080
                                initialDelaySeconds: 20
                                timeoutSeconds: 3
                                periodSeconds: 5

                                7. Restart and Verify

                                kubectl rollout restart deployment/web-deployment
                                kubectl get pods -w
                                """
            
            return one_shot_example + "\n\n" + base_prompt
        
        elif mode == "few-shot":
            pass

        else:
            raise ValueError("Invalid mode. Choose 'zero-shot', 'one-shot', or 'few-shot'")