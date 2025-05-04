Relevant Documentation Excerpts:


1.  ImagePullBackOff Meaning
"The status ImagePullBackOff means that a container could not start because Kubernetes could not pull a container image (for reasons such as invalid image name, or pulling from a private registry without imagePullSecret). The BackOff part indicates that Kubernetes will keep trying to pull the image, with an increasing back-off delay."

2. Causes of Image Pull Failures
"Kubernetes could not pull a container image for reasons such as invalid image name, or pulling from a private registry without imagePullSecret."

3. Using imagePullSecrets for Private Registries
"Kubernetes supports specifying container image registry keys on a Pod. imagePullSecrets must all be in the same namespace as the Pod. The referenced Secrets must be of type kubernetes.io/dockercfg or kubernetes.io/dockerconfigjson."

"This is the recommended approach to run containers based on images in private registries."

4. How imagePullPolicy Affects Image Pulling
"The imagePullPolicy for a container and the tag of the image affect when the kubelet attempts to pull (download) the specified image.
…
If you would like to always force a pull, you can do one of the following:

Set the imagePullPolicy of the container to Always.

Omit the imagePullPolicy and use :latest as the tag for the image to use; Kubernetes will set the policy to Always when you submit the Pod.

Omit the imagePullPolicy and the tag for the image to use; Kubernetes will set the policy to Always when you submit the Pod."





Step-by-step solution:


1. Verify Image Name and Tag

# Confirm the image exists in the registry
docker pull my-registry/app:v1.3

If this fails:

Fix typos in the image name/tag in your deployment YAML
Ensure the image is pushed to the registry

2. Configure imagePullSecrets for Private Registry

Create a Docker registry secret:
kubectl create secret docker-registry regcred \
  --docker-server=my-registry \
  --docker-username=<your-username> \
  --docker-password=<your-password> \
  --docker-email=<your-email>

Update your Pod/Deployment YAML:
spec:
  containers:
  - name: app
    image: my-registry/app:v1.3
  imagePullSecrets:
  - name: regcred  # Must match secret name

3. Validate Secret Configuration

# Verify secret exists in the same namespace
kubectl get secret regcred -o yaml

# Check if pod references the secret
kubectl describe pod <pod-name> | grep -A5 "Image Pull Secrets"

4. Force Image Pull (If Needed)
spec:
  containers:
  - name: app
    image: my-registry/app:v1.3
    imagePullPolicy: Always  # Force fresh pull

5. Apply Changes and Verify

kubectl delete pod <problem-pod>
kubectl apply -f updated-deployment.yaml
kubectl get pods -w  # Watch status transition
