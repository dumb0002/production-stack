#!/bin/bash

echo "Waiting for all llmstack pods to be in Running state..."

# Save output
VAR="${1#curl-}"
[ ! -d "output-$VAR" ] && mkdir "output-$VAR"
chmod -R 777 "output-$VAR"

# Print router logs
POD_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" | grep '^vllm-deployment-router')
kubectl wait --for=condition=ready pod/"$POD_NAME" --timeout=120s
kubectl logs -f "$POD_NAME" 2>&1 | tee "output-$VAR/router.log" &

# Loop to check if all llmstack-related pods are in the Running state
while true; do
    # Get all pods containing "vllm" in their name and extract their STATUS column
    pod_status=$(kubectl get pods --no-headers | grep "vllm" | awk '{print $3}' | sort | uniq)
    pod_ready=$(kubectl get pods --no-headers | grep "vllm" | awk '{print $2}' | sort | uniq)

    # If the only unique status is "Running", break the loop and continue
    if [[ "$pod_status" == "Running" ]] && [[ "$pod_ready" == "1/1" ]]; then
        echo "All llmstack pods are now Ready and in Running state."
        break
    fi

    echo "Not all pods are ready yet. Checking again in 5 seconds..."
    sleep 5
done

# Expose router service
kubectl patch service vllm-router-service -p '{"spec":{"type":"NodePort"}}'
ip=$(minikube ip)
port=$(kubectl get svc vllm-router-service -o=jsonpath='{.spec.ports[0].nodePort}')

sleep 5

bash ".github/$1.sh" "$ip" "$port"
