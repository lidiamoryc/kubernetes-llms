class K8sIssueQueryBuilder:
    def __init__(self, description="", logs="", events="", pod_yaml="",
                 pod_status=None, env=None, probe_config=None, volume_config=None):
        """
        Initialize the Kubernetes issue query builder with pod information.
        """
        self.description = description.strip()
        self.logs = logs.strip()

        # Handle events as either string or list
        if isinstance(events, list):
            self.events = "\n".join(events).strip()
        else:
            self.events = str(events).strip()

        self.pod_yaml = pod_yaml.strip()
        self.pod_status = pod_status
        self.env = env
        self.probe_config = probe_config
        self.volume_config = volume_config

    # Keep the existing extract_keywords and generate_query methods
    # You can enhance them later to use the new fields
    def extract_keywords(self):
        keywords = []

        # Pod status-based keywords
        if self.pod_status:
            keywords.append(self.pod_status)
            if self.pod_status == "CrashLoopBackOff":
                keywords.append("container restart")
                keywords.append("application crash")
            elif self.pod_status == "ImagePullBackOff":
                keywords.append("image pull failure")
                keywords.append("registry access")
            elif self.pod_status == "OOMKilled":
                keywords.append("memory limit")
                keywords.append("out of memory")
            elif self.pod_status == "CreateContainerConfigError":
                keywords.append("container configuration")
                keywords.append("config error")

        # Check for file read errors
        if "ENOENT" in self.logs or "no such file or directory" in self.logs:
            keywords.append("ENOENT")
            keywords.append("missing file")
            keywords.append("config file not found")

        # Check for configmap mount issues
        if "FailedMount" in self.events or "configmap" in self.events.lower():
            keywords.append("FailedMount")
            keywords.append("ConfigMap")
            if "not found" in self.events:
                keywords.append("ConfigMap not found")

        # Check for volume mount specifics
        if "volumeMounts" in self.pod_yaml:
            keywords.append("volumeMount")
        if "subPath" in self.pod_yaml:
            keywords.append("subPath")
        if "mountPath" in self.pod_yaml:
            keywords.append("mountPath")

        # Check for OOMKilled issues
        if "OOMKilled" in self.events or "exit code 137" in self.logs:
            keywords.append("OOMKilled")
            keywords.append("memory limit")
            keywords.append("out of memory")

        # Check for memory limits in pod yaml
        if "resources" in self.pod_yaml and "limits" in self.pod_yaml:
            keywords.append("resource limits")
            if "memory" in self.pod_yaml:
                keywords.append("memory limit")

        # Check for PodInitializing issues
        if "Init:" in self.events or "PodInitializing" in self.events:
            keywords.append("Init container")
            keywords.append("PodInitializing")

        # Check for probe failures
        if self.probe_config or "probe failed" in self.events.lower():
            keywords.append("probe failure")
            if "readiness" in self.events.lower():
                keywords.append("readiness probe")
            if "liveness" in self.events.lower():
                keywords.append("liveness probe")
            if self.probe_config:
                if "path" in str(self.probe_config):
                    keywords.append("http probe")
                if "timeoutSeconds" in str(self.probe_config):
                    keywords.append("probe timeout")

        # Check for database connection issues
        if "connection refused" in self.logs.lower() or "database unreachable" in self.logs.lower():
            keywords.append("database connection")
            keywords.append("connection refused")

        # Check for image pull issues
        if "ImagePullBackOff" in self.events or "Failed to pull image" in self.events:
            keywords.append("image pull failure")
            keywords.append("registry access")

        # Check for DNS/network issues
        if "nslookup" in self.logs or "could not resolve" in self.logs.lower() or "Failed to resolve" in self.events:
            keywords.append("DNS resolution")
            keywords.append("service discovery")

        return list(set(keywords))

    def generate_query(self):
        base_query = "Troubleshooting Kubernetes pod start failure"

        components = []

        if self.description:
            components.append(self.description)

        if self.pod_status:
            components.append(f"Pod status is {self.pod_status}.")

        # Add specific details based on pod status
        if self.pod_status == "CrashLoopBackOff":
            if "connection refused" in self.logs.lower() or "database unreachable" in self.logs.lower():
                components.append("Application repeatedly crashes due to database connection failures.")

        if self.pod_status == "ImagePullBackOff":
            components.append("Container image cannot be pulled from the registry.")

        if "ENOENT" in self.logs:
            components.append("App crashes because it cannot find the config file at the expected path.")

        if "configmap" in self.events.lower() and "not found" in self.events.lower():
            components.append("The ConfigMap specified in the pod spec is missing, causing a FailedMount event.")

        if "subPath" in self.pod_yaml:
            components.append("The config file is expected to be mounted using subPath.")

        if self.pod_status == "OOMKilled" or "OOMKilled" in self.events or "exit code 137" in self.logs:
            components.append(
                "The container is terminated due to exceeding its memory limit, resulting in OOMKilled status.")

        if "Init:" in self.events and "Error" in self.events:
            components.append("The pod is stuck in PodInitializing state because the init container is failing.")

        if "Readiness probe failed" in self.events:
            components.append("Container is not ready because the readiness probe is failing.")
            if self.probe_config and "path" in str(self.probe_config):
                path = self.probe_config.get("path", "")
                components.append(f"The readiness probe is checking the {path} endpoint.")

        keywords = ", ".join(self.extract_keywords())

        return f"{base_query}: {' '.join(components)} | Keywords: {keywords}"