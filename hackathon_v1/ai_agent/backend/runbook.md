# Runbook: Kubernetes Node Resource Exhaustion - mortgagelending Application

## Executive Summary

This runbook outlines the steps to resolve a P1 incident affecting the `mortgagelending` application due to insufficient resources (CPU and memory) on the Kubernetes cluster. The issue manifests as pods failing to schedule due to resource constraints, resulting in zero available nodes. This document provides a structured approach to diagnose, mitigate, and prevent future occurrences of this issue.

## Detailed Issue Description and Impact

On 4/10/2023, 4:30:00 pm, the `mortgagelending` application became unavailable.  Kubernetes reports "0/4 nodes are available: 2 Insufficient memory, 3 Insufficient cpu. preemption: 0/4 nodes are available: 4 No preemption victims found for incoming pod."  This indicates that the cluster nodes are exhausted of both memory and CPU resources, preventing new pods from scheduling, including those belonging to the `mortgagelending` application.  This results in application downtime and potential business disruption.

## Prerequisites

* **Tools:** `kubectl`, `kubectl top nodes`, `kubectl top pods`, `kubectl describe nodes`, `kubectl describe pods <pod-name>`
* **Access:** Kubernetes cluster administrator access.
* **Credentials:** Valid Kubernetes configuration (`kubeconfig`).


## Step-by-Step Implementation Instructions

**1. Identify Resource Bottlenecks:**

```bash
kubectl top nodes
kubectl top pods --all-namespaces
```

Analyze the output to pinpoint nodes and pods consuming the most resources.

**2. Check for Resource Requests and Limits:**

```bash
kubectl describe pods -n <mortgagelending-namespace> | grep -E "Resources:|Requests:|Limits:"
```

Verify if the `mortgagelending` pods have defined resource requests and limits.  Lack of these can lead to resource starvation.

**3. Scale Up Nodes (Horizontal Scaling):**

If resource requests and limits are appropriately set and the cluster is genuinely resource-constrained, scale up the number of nodes. This involves:

```bash
kubectl scale --replicas=<desired-number-of-replicas> deployment/<mortgagelending-deployment> -n <mortgagelending-namespace>  # If deployment
# OR
kubectl scale --replicas=<desired-number-of-replicas> statefulset/<mortgagelending-statefulset> -n <mortgagelending-namespace> # If statefulset
# OR
# Adjust your cluster autoscaler settings if enabled.
```

**4. Optimize Application Resource Usage (Vertical Scaling):**

If scaling up nodes is not immediately feasible or desired, consider optimizing resource usage within the `mortgagelending` application:

* **Reduce Replicas (if applicable):**  Temporarily reduce the number of replicas if the application can tolerate reduced capacity.
* **Code Optimization:** Investigate and optimize the application code for improved resource efficiency. This is a longer-term solution.
* **Resource Limit Adjustments:**  Adjust resource requests and limits for `mortgagelending` pods based on observed usage. Be cautious not to set limits too low, preventing proper application function.


## Verification Procedures

* **Pod Status:** Verify that `mortgagelending` pods are running and in a `Ready` state.
```bash
kubectl get pods -n <mortgagelending-namespace>
```
* **Application Functionality:** Test the `mortgagelending` application to ensure it is functioning correctly.
* **Resource Usage:** Monitor node and pod resource usage using `kubectl top nodes` and `kubectl top pods` to ensure resources are within acceptable levels.

## Rollback Instructions

If scaling up or resource adjustments cause unexpected issues:

* **Scale Down Nodes:**  Reduce the number of nodes back to the original count.
* **Revert Resource Changes:**  Revert any changes made to resource requests and limits for `mortgagelending` pods.
* **Rollback Deployment:** If code changes were deployed, roll back to the previous stable version of the application.

## Troubleshooting

* **Pods Stuck in Pending State:** Check for insufficient resources, incorrect resource requests/limits, or other scheduling constraints. Use `kubectl describe pod <pod-name>` for detailed information.
* **Nodes Not Joining the Cluster:** Verify network connectivity, kubelet configuration, and control plane health.
* **Persistent Volume Claims (PVCs) Not Binding:** Check for available storage and correct PVC configurations.
* **Application Errors:** Check application logs for specific errors and troubleshoot accordingly.  Use `kubectl logs <pod-name> -n <mortgagelending-namespace>`


This runbook provides a framework for addressing resource exhaustion issues. Remember to adapt the steps and commands to your specific environment and application configuration.  Regular monitoring and proactive resource management are crucial for preventing future incidents.
