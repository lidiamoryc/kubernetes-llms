#!/bin/bash
POD_NAME="web-pod"

# Generate filename components
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
POD_STATUS=$(kubectl get pod "$POD_NAME" -o jsonpath='{.status.phase}' | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_')
FILENAME="error_${POD_STATUS:-unknown}_${TIMESTAMP}.json"

# Capture diagnostic data with error handling
{
  echo '{"pod_status": "'"${POD_STATUS}"'"'
  
  # Logs with last 50 lines and timestamps
  echo '"logs": "'"$(kubectl logs "$POD_NAME" --tail=50 --timestamps 2>&1 | sed 's/"/\\"/g')"'"'
  
  # Events from last 1 hour
  echo '"events": ['$(
    kubectl get events \
      --field-selector involvedObject.name="$POD_NAME" \
      --sort-by=.lastTimestamp \
      --since=1h -o json 2>/dev/null | 
    jq -c '.items[].message'
  )']'
  
  # Environment variables from first container
  echo '"env": '"$(kubectl get pod "$POD_NAME" -o jsonpath='{.spec.containers[0].env}' 2>/dev/null)"
  
  # Readiness probe configuration
  echo '"probe_config": '"$(kubectl get pod "$POD_NAME" -o jsonpath='{.spec.containers[0].readinessProbe}' 2>/dev/null)"
} > "$FILENAME"
