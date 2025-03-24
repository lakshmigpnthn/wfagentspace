# Runbook: Kubernetes Pod Scheduling Failure - mortgagelending Application

## Executive Summary

This runbook outlines the steps to resolve a P1 incident where the `mortgagelending` application is unavailable due to insufficient resources (CPU and memory) in the Kubernetes cluster, preventing pod scheduling. The issue manifests as "0/4 nodes are available: 2 Insufficient memory, 3 Insufficient cpu. preemption: 0/4 nodes are available: 4 No preemption victims found for incoming pod."  This document provides a structured approach to diagnose, resolve, and verify the issue, including rollback steps if necessary.


## Detailed Issue Description and Impact

The `mortgagelending` application is currently unavailable because Kubernetes cannot schedule its pods. The cluster reports insufficient CPU and memory resources on all four nodes.  Preemption is also failing, indicating that no lower-priority pods can be evicted to make room for the `mortgagelending` pods. This outage is impacting all users of the `mortgagelending` application, potentially disrupting loan processing and causing significant business impact.


## Prerequisites

* **Tools:** `kubectl` command-line tool, access to Kubernetes cluster monitoring tools (e.g., Prometheus, Grafana).
* **Access:**  `kubectl` configured with access to the affected Kubernetes cluster.  Sufficient permissions to create, delete, and modify deployments, pods, and nodes.
* **Credentials:** Valid credentials for accessing the Kubernetes cluster and monitoring tools.


## Step-by-Step Implementation Instructions

**1. Identify Resource Bottlenecks:**

```bash
kubectl top nodes
kubectl top pods -n <mortgagelending-namespace>
```

**2. Analyze Pod Resource Requests and Limits:**

```bash
kubectl describe deployment <mortgagelending-deployment> -n <mortgagelending-namespace>
kubectl get pods -n <mortgagelending-namespace> -o json | jq '.items[].spec.containers[].resources'
```

**3. Option 1: Scale Up Nodes (Preferred):**

* **Increase Node Count:**  If cluster autoscaler is enabled, verify its configuration and trigger it manually if necessary. If not, manually add more nodes with sufficient resources.
    ```bash
    # Example using a cloud provider CLI (replace with your provider's command)
    gcloud container clusters resize <cluster-name> --size=<new-size>
    ```
* **Monitor Node Readiness:** Ensure the new nodes join the cluster and become ready.
    ```bash
    kubectl get nodes
    ```

**4. Option 2: Optimize Resource Requests and Limits (If Scaling Up is Not Immediately Feasible):**

* **Adjust Resource Requests/Limits:** If analysis reveals overly generous resource allocations, reduce them to more realistic values. Modify the deployment YAML and apply the changes.
    ```bash
    kubectl edit deployment <mortgagelending-deployment> -n <mortgagelending-namespace>
    ```
    (Update `resources.requests` and `resources.limits` for each container)
* **Restart Pods:**  Restart the `mortgagelending` pods to apply the new resource limits.
    ```bash
    kubectl rollout restart deployment <mortgagelending-deployment> -n <mortgagelending-namespace>
    ```

**5. Option 3: Terminate Non-Essential Pods (Last Resort):**

* **Identify Low-Priority Pods:** Using `kubectl top pods` and knowledge of application dependencies, identify less critical pods consuming significant resources.
* **Terminate Pods:**  Terminate the identified pods to free up resources.
    ```bash
    kubectl delete pod <pod-name> -n <namespace>
    ```
    **Caution:** Ensure terminating these pods does not cause cascading failures.


## Verification Procedures

* **Check Pod Status:** Verify that `mortgagelending` pods are running and in a `Ready` state.
    ```bash
    kubectl get pods -n <mortgagelending-namespace>
    ```
* **Application Health Check:**  Perform application-specific health checks (e.g., accessing the application's endpoint) to ensure it's functioning correctly.
* **Monitor Resource Utilization:**  Continue monitoring resource utilization to ensure the issue is resolved and doesn't reoccur.


## Rollback Instructions

* **Option 1 (Scaling Up):** If scaling up caused unintended issues, reduce the node count back to the original size.
* **Option 2 (Resource Optimization):** Revert the deployment YAML to the previous version with the original resource requests and limits.
* **Option 3 (Pod Termination):** Restart any terminated non-essential pods.


## Troubleshooting

* **Pods Stuck in Pending State:** Check for persistent volume claims (PVCs) issues, insufficient quota, or other scheduling constraints.
* **Nodes Not Joining Cluster:** Verify network connectivity, DNS resolution, and cloud provider configuration.
* **Application Errors After Resource Adjustments:** Check application logs for errors related to resource constraints.  The application might need code changes to handle lower resource limits effectively.
* **Preemption Still Failing:** Review Pod PriorityClass settings and ensure that the `mortgagelending` pods have a sufficiently high priority.  Check for resource quotas that might be preventing preemption.


This runbook provides a starting point.  Adapt and expand it based on your specific environment and application requirements. Remember to document any deviations or additional steps taken during the incident resolution. 
