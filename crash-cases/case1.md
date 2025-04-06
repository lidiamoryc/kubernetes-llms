A Node.js web app deployed via a Deployment in Kubernetes. It expects a config file injected via a ConfigMap, mounted as a volume at /app/config.json.

The app fails to start after deployment. You want the LLM to help diagnose and suggest a fix.

**kubectl logs <pod>**
2025-04-06T14:33:01Z [INFO] App starting...
2025-04-06T14:33:01Z [ERROR] Failed to read config file at /app/config.json
Error: ENOENT: no such file or directory, open '/app/config.json'
    at Object.openSync (fs.js:498:3)
    at readFileSync (fs.js:394:35)
    at loadConfig (/app/server.js:12:15)

**kubectl describe pod <pod>**
Events:
  Normal   Scheduled      Successfully assigned app/web-app-648f7 to node-1
  Normal   Pulled         Pulled image "myregistry/web-app:latest"
  Normal   Created        Created container web
  Normal   Started        Started container web
  Warning  FailedMount    Unable to mount volumes for pod "web-app-648f7":
                         configmap "web-app-config" not found
  Warning  FailedSync     Error syncing pod


**POD YAML (Partial) **
volumeMounts:
  - name: config
    mountPath: /app/config.json
    subPath: config.json
volumes:
  - name: config
    configMap:
      name: web-app-config
