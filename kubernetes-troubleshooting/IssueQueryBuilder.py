class K8sIssueQueryBuilder:
    def __init__(self, description="", logs="", events="", pod_yaml=""):
        self.description = description.strip()
        self.logs = logs.strip()
        self.events = events.strip()
        self.pod_yaml = pod_yaml.strip()

    def extract_keywords(self):
        keywords = []

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

        return list(set(keywords))

    def generate_query(self):
        base_query = "Troubleshooting Kubernetes pod start failure"

        components = []

        if self.description:
            components.append(self.description)

        if "ENOENT" in self.logs:
            components.append("App crashes because it cannot find the config file at the expected path.")

        if "configmap" in self.events.lower() and "not found" in self.events.lower():
            components.append("The ConfigMap specified in the pod spec is missing, causing a FailedMount event.")

        if "subPath" in self.pod_yaml:
            components.append("The config file is expected to be mounted at /app/config.json using subPath.")

        keywords = ", ".join(self.extract_keywords())

        return f"{base_query}: {' '.join(components)} | Keywords: {keywords}"
