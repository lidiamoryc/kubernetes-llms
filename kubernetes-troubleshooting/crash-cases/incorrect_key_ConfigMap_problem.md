A Python web service deployed via a Deployment in Kubernetes.

It expects configuration values (e.g., database credentials) injected via a ConfigMap as environment variables.

The app fails to connect to the database after deployment - there is an incorrect key reference in environment variables via ConfigMap.

**kubectl logs <pod>**
```
2025-04-06T10:11:15Z [INFO] Starting Flask app...
2025-04-06T10:11:15Z [ERROR] Missing environment variable: DB_HOST
Traceback (most recent call last):
  File "/app/server.py", line 8, in <module>
    db_host = os.environ["DB_HOST"]
KeyError: 'DB_HOST'
```

**kubectl describe pod <pod>**
```
Events:
  Normal   Scheduled      Successfully assigned app/flask-api-75dbf to node-2
  Normal   Pulled         Pulled image "registry/flask-api:latest"
  Normal   Created        Created container flask-api
  Normal   Started        Started container flask-api
```

**POD YAML (Partial)**
```
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
```