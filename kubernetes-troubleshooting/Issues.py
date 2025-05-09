import json
import os
from glob import glob

from IssueQueryBuilder import K8sIssueQueryBuilder

config_map_issue = K8sIssueQueryBuilder(
    description="Node.js app fails after deployment; expects /app/config.json from ConfigMap.",
    logs="""
2025-04-06T14:33:01Z [INFO] App starting...
2025-04-06T14:33:01Z [ERROR] Failed to read config file at /app/config.json
Error: ENOENT: no such file or directory, open '/app/config.json'
    at Object.openSync (fs.js:498:3)
    at readFileSync (fs.js:394:35)
    at loadConfig (/app/server.js:12:15)
""",
    events="""
Warning  FailedMount    Unable to mount volumes for pod "web-app-648f7":
                       configmap "web-app-config" not found
Warning  FailedSync     Error syncing pod
""",
    pod_yaml="""
volumeMounts:
  - name: config
    mountPath: /app/config.json
    subPath: config.json
volumes:
  - name: config
    configMap:
      name: web-app-config
"""
)

config_map_query = config_map_issue.generate_query()
print("\n🔍 Generated Query for Embedding:\n")
print(config_map_query)


incorrect_key_config_map_issue = K8sIssueQueryBuilder(
    description="Python Flask app fails to start; expects DB_HOST environment variable from ConfigMap.",
    logs="""
2025-04-06T10:11:15Z [INFO] Starting Flask app...
2025-04-06T10:11:15Z [ERROR] Missing environment variable: DB_HOST
Traceback (most recent call last):
  File "/app/server.py", line 8, in <module>
    db_host = os.environ["DB_HOST"]
KeyError: 'DB_HOST'
""",
    events="""
Normal   Scheduled      Successfully assigned app/flask-api-75dbf to node-2
Normal   Pulled         Pulled image "registry/flask-api:latest"
Normal   Created        Created container flask-api
Normal   Started        Started container flask-api
""",
    pod_yaml="""
env:
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: database_host

volumes:
  - name: config-volume
    configMap:
      name: app-config

volumeMounts:
  - name: config-volume
    mountPath: /etc/app/config
    readOnly: true
"""
)

incorrect_key_config_map_query = incorrect_key_config_map_issue.generate_query()
print("\n🔍 Generated Query for Embedding:\n")
print(incorrect_key_config_map_query)


# Wczytywanie problemów z plików JSON
def load_issues_from_database():
    database_path = "/Users/damianotto/PycharmProjects/kubernetes-llms/kubernetes-troubleshooting/crash-cases/hardcoded-database"
    issue_files = glob(os.path.join(database_path, "*.json"))
    print(f"Found {len(issue_files)} issue files in {database_path}")
    issues = {}

    for file_path in issue_files:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Nazwa pliku bez rozszerzenia jako klucz
            issue_name = os.path.splitext(os.path.basename(file_path))[0]

            # Konwersja listy zdarzeń na tekst
            events_text = ""
            if "events" in data and isinstance(data["events"], list):
                events_text = "\n".join(data["events"])
            elif "events" in data:
                events_text = str(data["events"])

            # Tworzymy YAML dla poda na podstawie dostępnych danych
            pod_yaml_parts = []

            # Handle environment variables (both array and object formats)
            if "env" in data:
                env_yaml = ""
                if isinstance(data["env"], list):
                    for env_var in data["env"]:
                        if isinstance(env_var, dict) and "name" in env_var and "value" in env_var:
                            env_yaml += f"  - name: {env_var['name']}\n    value: {env_var['value']}\n"
                elif isinstance(data["env"], dict):
                    for key, value in data["env"].items():
                        env_yaml += f"  - name: {key}\n    value: {str(value)}\n"

                if env_yaml:
                    pod_yaml_parts.append(f"env:\n{env_yaml}")

            # Handle volume configuration if present
            if "volume_config" in data and isinstance(data["volume_config"], dict):
                vol_config = data["volume_config"]
                vol_yaml = "volumeMounts:\n"
                vol_yaml += f"  - name: config\n"

                if "mountPath" in vol_config:
                    vol_yaml += f"    mountPath: {vol_config['mountPath']}\n"
                if "subPath" in vol_config:
                    vol_yaml += f"    subPath: {vol_config['subPath']}\n"

                vol_yaml += "volumes:\n"
                vol_yaml += "  - name: config\n"

                if "configMapRef" in vol_config:
                    vol_yaml += "    configMap:\n"
                    vol_yaml += f"      name: {vol_config['configMapRef']}\n"

                pod_yaml_parts.append(vol_yaml)

            # Handle probe configuration if present
            if "probe_config" in data and isinstance(data["probe_config"], dict):
                probe = data["probe_config"]
                probe_yaml = "readinessProbe:\n"

                if "path" in probe and "port" in probe:
                    probe_yaml += "  httpGet:\n"
                    probe_yaml += f"    path: {probe['path']}\n"
                    probe_yaml += f"    port: {probe['port']}\n"

                if "initialDelaySeconds" in probe:
                    probe_yaml += f"  initialDelaySeconds: {probe['initialDelaySeconds']}\n"
                if "timeoutSeconds" in probe:
                    probe_yaml += f"  timeoutSeconds: {probe['timeoutSeconds']}\n"

                pod_yaml_parts.append(probe_yaml)

            # Combine all YAML parts
            pod_yaml = "\n".join(pod_yaml_parts)

            # Create description from available fields
            description = data.get("summary", "")
            if not description and "pod_status" in data:
                description = f"Pod in {data['pod_status']} state"
                if issue_name:
                    description += f" with {issue_name} issue"

            # Create issue object
            issue = K8sIssueQueryBuilder(
                description=data.get("summary", ""),
                logs=data.get("logs", ""),
                events=data.get("events", []),
                pod_yaml=pod_yaml,
                pod_status=data.get("pod_status"),
                env=data.get("env"),
                probe_config=data.get("probe_config"),
                volume_config=data.get("volume_config")
            )

            # Generate query and save
            issue_query = issue.generate_query()
            issues[issue_name] = {
                "issue": issue,
                "query": issue_query
            }

            print(f"\n🔍 Generated Query for Embedding ({issue_name}):\n")
            print(issue_query)

        except Exception as e:
            print(f"Error loading issue from {file_path}: {e}")

    return issues


# Wczytanie wszystkich problemów z bazy danych
database_issues = load_issues_from_database()

