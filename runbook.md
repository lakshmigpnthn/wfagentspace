# Runbook: Resolve Replica Mismatch for mortgagelending Deployment

## Executive Summary

This runbook outlines the steps to resolve a replica mismatch for the `mortgagelending` deployment. Currently, the deployment specifies 1 replica, but 2 are running. This discrepancy can lead to resource wastage and potential inconsistencies. This runbook provides a structured approach to correct the number of replicas to the desired state, including verification and rollback procedures.

## Detailed Issue Description and Impact

The `mortgagelending` deployment is currently running 2 replicas despite being configured for 1. This over-provisioning can result in:

* **Increased resource consumption:** Unnecessary pods consume CPU, memory, and other resources.
* **Potential data inconsistencies:** If the application is not designed for multiple replicas, this can lead to data conflicts or unexpected behavior.
* **Cost implications:**  Running extra replicas can increase cloud infrastructure costs.

The goal is to reduce the number of replicas to 1, matching the desired state defined in the deployment configuration.

## Prerequisites

* **Kubectl:** Access to a `kubectl` client configured to interact with the affected Kubernetes cluster.
* **Cluster Admin/Edit access:**  Sufficient permissions to modify deployments within the namespace where `mortgagelending` resides.
* **Monitoring access:** Access to monitoring tools to observe the application's health and resource usage during and after the fix.
* **Deployment configuration:** Access to the deployment's YAML file or knowledge of the deployment's name and namespace.


## Implementation Instructions

1. **Identify the deployment:**
    ```bash
    kubectl get deployments -n <namespace> | grep mortgagelending
    ```
    Replace `<namespace>` with the namespace where the deployment resides.

2. **Scale down the deployment:**
    ```bash
    kubectl scale deployment mortgagelending --replicas=1 -n <namespace>
    ```

3. **Observe the scaling process:**
    ```bash
    kubectl get pods -n <namespace> -w | grep mortgagelending
    ```
    This command will show the pods terminating until only one remains.

## Verification Procedures

1. **Confirm replica count:**
    ```bash
    kubectl get deployments mortgagelending -n <namespace> | grep mortgagelending
    ```
    Verify that the `DESIRED` and `CURRENT` replica counts are both 1.

2. **Check pod status:**
    ```bash
    kubectl get pods -n <namespace> | grep mortgagelending
    ```
    Ensure that the single remaining pod is in a `Running` and `Ready` state.

3. **Monitor application health:** Use your monitoring tools to confirm that the application is functioning correctly with the reduced replica count. Verify metrics like CPU usage, memory consumption, and request latency.


## Rollback Instructions

If the application encounters issues after scaling down, you can quickly revert to the previous state:

1. **Scale up the deployment:**
    ```bash
    kubectl scale deployment mortgagelending --replicas=2 -n <namespace>
    ```
2. **Monitor the scaling process and application health:**  Repeat the verification steps to ensure the application returns to a healthy state.
3. **Investigate the root cause:**  If the rollback was necessary, investigate the reason why the application couldn't function with a single replica. Potential issues include resource limitations, application bugs, or misconfigurations.

## Troubleshooting

**Issue:** Scaling down fails with an error message.

* **Possible Cause 1:** Insufficient permissions.
    * **Solution:** Ensure the user or service account used by `kubectl` has sufficient permissions to modify deployments in the target namespace.
* **Possible Cause 2:**  Underlying issues with the Kubernetes cluster.
    * **Solution:**  Check the Kubernetes cluster's health and resource availability. Consult cluster logs or contact your cluster administrator.

**Issue:** Application performance degrades after scaling down.

* **Possible Cause:** Single replica not sufficient to handle the workload.
    * **Solution:**  Consider increasing the resources allocated to the single replica (CPU, memory) or re-evaluate the desired replica count based on application requirements.  Investigate using Horizontal Pod Autoscaler (HPA) for dynamic scaling.


**Issue:** Pod continuously restarts after scaling down.

* **Possible Cause:**  Application error or resource limitations within the pod.
    * **Solution:** Check the pod logs (`kubectl logs <pod-name> -n <namespace>`) for error messages. Verify resource requests and limits defined in the deployment configuration.




This runbook provides a comprehensive guide to address the replica mismatch issue. Remember to adapt the namespace and deployment name as needed for your specific environment.  Thorough verification and monitoring are crucial for a successful resolution. 
