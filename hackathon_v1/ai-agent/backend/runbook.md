# Runbook: Resolving Redundant Replica for mortgagelending Deployment

## Executive Summary

This runbook outlines the steps to resolve an issue where the `mortgagelending` deployment has two available replicas despite being configured for one. This redundancy can lead to resource wastage and potential inconsistencies.  This document provides a structured approach to safely reduce the replica count to the desired state.

## Detailed Issue Description and Impact

On 1/10/2023 at 3:45:00 pm, the `mortgagelending` deployment was observed to have two running replicas while the desired replica count is one.  This extra replica consumes unnecessary resources and potentially introduces data inconsistencies if not synchronized properly. This issue is classified as P1 due to the potential for resource exhaustion and data integrity concerns.

## Prerequisites

* **Tools:**  `kubectl` command-line tool.
* **Access:**  Kubernetes cluster access with sufficient permissions to manage deployments in the namespace where `mortgagelending` is deployed.
* **Credentials:** Valid Kubernetes configuration file (`kubeconfig`).


## Step-by-Step Implementation Instructions


1. **Verify Current Replica Count:**
   ```bash
   kubectl get deployment mortgagelending -n <namespace>
   ```
   Replace `<namespace>` with the namespace where your deployment resides. Confirm that `REPLICAS` shows `1/2` or similar, indicating the discrepancy.

2. **Scale Down the Deployment:**
   ```bash
   kubectl scale deployment mortgagelending --replicas=1 -n <namespace>
   ```
   This command instructs Kubernetes to scale down the deployment to the desired replica count of one.

3. **Monitor the Scaling Process:**
   ```bash
   kubectl rollout status deployment/mortgagelending -n <namespace>
   ```
   Observe the output to ensure the scaling down process completes successfully.  Wait until the rollout is complete before proceeding.

4. **Confirm Replica Count:**
   ```bash
   kubectl get deployment mortgagelending -n <namespace>
   ```
    Verify that the `REPLICAS` count now shows `1/1`.


## Verification Procedures

* **Check Pod Status:**
   ```bash
   kubectl get pods -l app=mortgagelending -n <namespace>
   ```
   Ensure only one pod is running and in a `Running` or `Ready` state.  Replace `app=mortgagelending` with the appropriate label selector if different.

* **Application Health Check:**  Perform application-specific health checks (e.g., accessing the application endpoint, running integration tests) to confirm that the application is functioning correctly with a single replica.


## Rollback Instructions

If the scaling down causes issues, you can quickly scale back up to two replicas:

```bash
kubectl scale deployment mortgagelending --replicas=2 -n <namespace>
```

Monitor the rollout status as described in step 3.  Investigate the root cause of the issue after restoring the original replica count.

## Troubleshooting

**Issue:** `kubectl scale` command fails with permission denied.

**Solution:** Ensure your kubeconfig has the necessary permissions to modify deployments in the target namespace. Contact your cluster administrator if needed.


**Issue:**  Scaling down completes, but the application is not functioning correctly.

**Solution:**  Check application logs for errors:
```bash
kubectl logs -l app=mortgagelending -n <namespace>
```
Review recent code changes or configuration updates that might have introduced issues. Consider rolling back to a previous working version of the application.


**Issue:**  Scaling down takes an unusually long time.

**Solution:** Investigate potential resource constraints on the cluster. Check pod events for any issues during termination:
```bash
kubectl describe pod <pod-name> -n <namespace>
```
Monitor cluster resource usage to identify bottlenecks.


This runbook provides a detailed guide for resolving the redundant replica issue. If you encounter problems not covered here, escalate the issue to the appropriate support team.  Remember to update this runbook with any new information or troubleshooting steps learned during future incidents.
