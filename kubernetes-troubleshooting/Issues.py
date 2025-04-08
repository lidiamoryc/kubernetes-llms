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
