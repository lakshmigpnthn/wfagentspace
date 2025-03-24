```bash
#!/bin/bash

# Script to resolve the issue of excess replicas for the mortgagelending deployment.

# --- Variables ---
DEPLOYMENT_NAME="mortgagelending"
NAMESPACE="default" # Replace with the correct namespace if different

# --- Functions ---

function log_info() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") [INFO] $*"
}

function log_error() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") [ERROR] $*" >&2
}

function check_kubectl() {
  if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. Please install kubectl."
    exit 1
  fi
}


# --- Main Script ---

check_kubectl

log_info "Starting remediation for deployment: $DEPLOYMENT_NAME in namespace: $NAMESPACE"


# 1. Scale down the deployment to 0 replicas to stop the service.  This is generally safer than directly stopping pods.
log_info "Scaling down deployment $DEPLOYMENT_NAME to 0 replicas..."
kubectl scale deployment "$DEPLOYMENT_NAME" --replicas=0 -n "$NAMESPACE" || { log_error "Failed to scale down deployment."; exit 1; }

# Wait for the pods to terminate.  This is crucial.
log_info "Waiting for pods to terminate..."
while kubectl get pods -n "$NAMESPACE" -l app="$DEPLOYMENT_NAME" | grep -q Running; do
    sleep 5
    log_info "Still waiting for pods to terminate..."
done


# 2. Apply necessary fixes (placeholders for actual fixes). 
#    In a real scenario, this section would contain commands to address the root cause
#    of the extra replicas. This might involve:
#    - Checking the deployment configuration for errors.
#    - Investigating replica controllers or replica sets.
#    - Examining Horizontal Pod Autoscalers (HPAs).
#    - Rolling back to a previous deployment version if necessary.


log_info "Applying fixes..."

# Example: Checking HPA (replace with your actual fix)
kubectl get hpa -n "$NAMESPACE" -l app="$DEPLOY