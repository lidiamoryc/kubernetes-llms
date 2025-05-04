Relevant Documentation Excerpts:


1. ConfigMap Mounting Requirements
"When mounting a ConfigMap key as a file using subPath, the key must exist in the ConfigMap's data field. If the key is missing or the ConfigMap doesn't exist, the mount fails with CreateContainerConfigError."

2. Error Cause Identification
"CreateContainerConfigError occurs when a Pod references a non-existent ConfigMap. Verify the ConfigMap exists in the same namespace as the Pod with kubectl get configmap <name>."

3. Proper Volume Configuration
"To mount a single ConfigMap key as a file:

volumes:
- name: config
  configMap:
    name: web-app-config
    items:  # Explicit key-to-file mapping
    - key: config.json  # Must exist in ConfigMap
      path: config.json
Without items, the entire ConfigMap is mounted as a directory, not individual files."





Step-by-Step Solution:


1.   Verify/Create the Missing ConfigMap

kubectl get configmap/web-app-config -n <namespace>

If missing, create it

apiVersion: v1
kind: ConfigMap
metadata:
  name: web-app-config
  namespace: <your-namespace>
data:
  config.json: |  # Key must match subPath
    { "your": "configuration" }

2. Fix Volume Mount Configuration

 volumes:
 - name: config
   configMap:
     name: web-app-config
+    items:
+    - key: config.json  # Must match ConfigMap key
+      path: config.json

 volumeMounts:
 - name: config
-  mountPath: /app/config.json  #  File path
+  mountPath: /app  #  Directory path
   subPath: config.json


3. Resolve File Conflicts

Check for pre-existing files in container image:
kubectl exec <pod> -- ls -la /app

If /app/config.json exists:
# In Dockerfile
RUN rm -f /app/config.json  # Remove conflicting file

4. Apply Changes

kubectl apply -f updated-deployment.yaml
kubectl delete pod <problem-pod>  # Force recreation

5. Verification:

Check pod status: kubectl get pods -w

Verify mounted file: kubectl exec <new-pod> -- cat /app/config.json

Inspect events: kubectl describe pod <new-pod> | grep -A20 Events
