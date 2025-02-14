#!/bin/bash

# This script should be called from the root dir of the cloned repository.

NAMESPACE="serverless-workstream"
DEPLOYMENT_NAME="vllm-test"
LABEL="app=vllm-test"
CLEANUP=${CLEANUP:-false}

# For MacOS, `brew install coreutils` can make gdate available, if necessary
START_TIME=$(gdate +%s%3N)

kubectl apply -f ./perf-test/pod-startup/vllm-pvc-no-template.yaml -n $NAMESPACE
kubectl apply -f ./perf-test/pod-startup/vllm-deployment-no-template.yaml -n $NAMESPACE

# Wait until at least one pod exists before proceeding
while [[ -z $(kubectl get pods -n $NAMESPACE -l $LABEL -o jsonpath='{.items[0].metadata.name}') ]]; do
    sleep 0.1
done

# Get a pod name
POD_NAME=$(kubectl get pods -n $NAMESPACE -l $LABEL -o jsonpath='{.items[0].metadata.name}')

# Wait for the pod to be "Running"
kubectl wait --for=jsonpath='{.status.phase}'=Running pod/$POD_NAME -n $NAMESPACE --timeout=3600s

# Record the end time in milliseconds
END_TIME=$(gdate +%s%3N)

# Calculate startup latency in milliseconds
LATENCY_MS=$((END_TIME - START_TIME))

# Convert milliseconds to seconds and show it
LATENCY_SEC=$(echo "scale=3; $LATENCY_MS / 1000" | bc)
echo "Pod startup latency: ${LATENCY_SEC} seconds"

# Optional cleanup
if [ "$CLEANUP" = "true" ]; then
    kubectl delete -f ./perf-test/pod-startup/vllm-deployment-no-template.yaml -n $NAMESPACE --wait
    kubectl delete -f ./perf-test/pod-startup/vllm-pvc-no-template.yaml -n $NAMESPACE --wait
fi
