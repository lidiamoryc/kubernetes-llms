#!/bin/bash

POD_NAME="your-pod-name"
NODE_NAME="your-node-name"
OUTPUT_DIR="diag"
INTERVAL=30

mkdir -p "$OUTPUT_DIR"
echo "Continuous diagnostics running... Press Ctrl+C to stop."
echo "Saving to folder: $OUTPUT_DIR"
echo "Target pod: $POD_NAME | Node: $NODE_NAME"
echo ""

while true; do
  TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%SZ")
  FILE="$OUTPUT_DIR/snapshot_$TIMESTAMP.json"

  echo "Capturing snapshot at $TIMESTAMP..."

  # collecting info
  PODS=$(kubectl get pods -o wide --no-headers | awk '{$1=$1}1' | sed 's/  */,/g' | jq -R -s -c 'split("\n")[:-1]')
  DESCRIBE=$(kubectl describe pod "$POD_NAME" | jq -Rs .)
  LOGS=$(kubectl logs "$POD_NAME" | jq -Rs .)
  EVENTS=$(kubectl get events --sort-by=.lastTimestamp | jq -Rs .)
  TOP_PODS=$(kubectl top pods | jq -Rs .)
  NODE_DESC=$(kubectl describe node "$NODE_NAME" | jq -Rs .)

  # combining into JSON
  jq -n \
    --arg timestamp "$TIMESTAMP" \
    --argjson pods "$PODS" \
    --arg describe "$DESCRIBE" \
    --arg logs "$LOGS" \
    --arg events "$EVENTS" \
    --arg top_pods "$TOP_PODS" \
    --arg node_desc "$NODE_DESC" \
    '{
      timestamp: $timestamp,
      pods: $pods,
      describe: $describe,
      logs: $logs,
      events: $events,
      top_pods: $top_pods,
      node: $node_desc
    }' > "$FILE"

  echo "Snapshot saved: $FILE"
  echo "Waiting $INTERVAL seconds..."
  sleep $INTERVAL
done
