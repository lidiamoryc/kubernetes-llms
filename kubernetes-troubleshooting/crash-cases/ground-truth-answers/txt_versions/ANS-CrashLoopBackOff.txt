Relevant Documentation Excerpts:


1. Service Discovery & DNS
"Pods should reference Services by their DNS name (<service>.<namespace>.svc.cluster.local), not static IPs. IPs are ephemeral in Kubernetes clusters."

2. CrashLoopBackOff Definition
"A pod enters CrashLoopBackOff state when its containers repeatedly crash. Check logs with kubectl logs --previous to identify the root cause."

3. Readiness Probe Best Practices
*"For applications with slow startup:

Set initialDelaySeconds longer than maximum initialization time

timeoutSeconds should exceed expected request processing time"*

4. Endpoint Verification
*"Validate service-to-pod mapping with:

kubectl get endpoints <service-name>  
Empty results indicate no healthy pods match service selectors."*

5. DNS Resolution Troubleshooting
*"Debug DNS issues from within pods using:

kubectl exec -it <pod> -- nslookup <service>  
Failure indicates CoreDNS issues or missing service."*





Step by step solution:


1. Replace Static IP with Service DNS Name

# Before
env: {"DB_HOST": "10.0.0.5"}

# After
env:
- name: DB_HOST
  value: "database-service.default.svc.cluster.local"  # Service DNS format

2. Verify Database Service Exists

kubectl get svc database-service -n default

If missing, create the service:

apiVersion: v1
kind: Service
metadata:
  name: database-service
  namespace: default
spec:
  selector:
    app: database  # Must match database pod labels
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432

3. Check Service Endpoints

kubectl get endpoints database-service -o wide

Expected Output: ENDPOINTS 10.0.0.5:5432

If empty: Database pods aren't properly labeled or running

4. Test DNS Resolution

kubectl exec web-pod -- nslookup database-service.default.svc.cluster.local

Success: Returns database service IP

Failure: Indicates CoreDNS issues or missing service

5. Validate Network Connectivity

kubectl exec web-pod -- nc -zv database-service.default.svc.cluster.local 5432

Connection refused: Verify database pod is running and listening on 5432

Timeout: Check network policies and firewall rules

6. Adjust Readiness Probes

readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 20  # Allow DB connection setup
  timeoutSeconds: 3        # From 1 second
  periodSeconds: 5

7. Verification

kubectl rollout restart deployment/web-deployment
kubectl get pods -w  # Watch for stable status




