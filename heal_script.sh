```bash
#!/bin/bash

# Script to resolve the issue of excess replicas for the mortgagelending deployment

# --- Variables ---
NAMESPACE="default"  # Replace with the actual namespace if different
DEPLOYMENT_NAME="mortgagelending"
DESIRED_REPLICAS=1

# --- 1. Stop affected services ---
echo "Stopping the $DEPLOYMENT_NAME deployment..."
kubectl scale deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" --replicas=0
# Wait for pods to terminate gracefully (adjust timeout as needed)
kubectl rollout status deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=60s || true 

# --- 2. Apply necessary fixes ---
# In this case, the fix is to ensure the desired replica count is correctly set.
# If there were other underlying issues (e.g., replicaset controller problems, 
# resource constraints preventing scale down), address them here.  This might involve:
# - Deleting extra replicasets manually:
#   kubectl delete replicaset <replicaset-name> -n "$NAMESPACE"
# - Investigating and resolving resource limits/requests:
#   kubectl describe deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE"
# - Checking the deployment configuration for any errors:
#   kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o yaml

echo "Ensuring desired replica count is $DESIRED_REPLICAS..."
kubectl scale deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" --replicas=$DESIRED_REPLICAS



# --- 3. Restart the services ---
echo "Scaling the $DEPLOYMENT_NAME deployment back to $DESIRED_REPLICAS replicas..."
kubectl scale deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" --replicas=$DESIRED_REPLICAS
# Verify the rollout is successful
kubectl rollout status deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=60s


# --- 4. Verification (Optional but highly recommended) ---
echo "Verifying the number of running pods..."
kubectl get pods -n "$NAMESPACE" -l "app=$DEPLOYMENT_NAME"  # Check labels match your deployment
RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE"