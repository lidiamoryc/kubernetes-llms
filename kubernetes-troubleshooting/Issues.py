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
