# Runbook: Application Server Crash Under High Load

## Executive Summary

This runbook outlines the procedures to address the application server crashes occurring under high load (exceeding 500 concurrent users).  The issue surfaced after the latest feature update and manifests as "Out of Memory" errors in the server logs. The resolution involves increasing server resources, implementing connection throttling, fixing a memory leak, adding monitoring and alerts, and implementing load balancing.

## Detailed Issue Description and Impact

The application server becomes unresponsive and crashes when the number of concurrent users exceeds 500.  This results in complete application downtime, impacting all users. The "Out of Memory" errors in the server logs indicate resource exhaustion as the root cause. This issue started after deploying the recent feature update, suggesting the update introduced a bug or increased resource consumption.  The impact of this issue is severe, leading to loss of productivity and potential revenue loss.

## Prerequisites

* **Tools:** SSH client, Text editor, Application server administration tools
* **Access:** Root/Administrator access to the application server, Load balancer administration access
* **Credentials:** Application server credentials, Load balancer credentials, Monitoring system credentials


## Step-by-Step Implementation Instructions

**Phase 1: Immediate Mitigation - Increase Server Memory and Throttle Connections**

1. **Increase JVM Heap Size:**
    ```bash
    ssh <user>@<app_server_ip>
    sudo nano /etc/appserver/config.xml 
    # Locate the JVM heap settings and modify:
    # <jvm-options>-Xmx2g</jvm-options>  TO
    # <jvm-options>-Xmx4g</jvm-options>
    sudo systemctl restart appserver
    ```

2. **Implement Connection Throttling:**
    ```bash
    # Assuming using a web server like Apache or Nginx
    ssh <user>@<app_server_ip>
    sudo nano /etc/nginx/nginx.conf  # or /etc/apache2/apache2.conf
    # Add/modify configuration for connection limiting and queuing (example for Nginx):
    # http {
    #   ...
    #   limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    #   server {
    #       ...
    #       limit_conn conn_limit 400;
    #       ...
    #   }
    # }
    sudo systemctl restart nginx  # or apache2
    ```

**Phase 2: Long-Term Solution - Code Fix, Monitoring, and Load Balancing**

3. **Fix Memory Leak in User Session Handling:**
    ```bash
    ssh <user>@<app_server_ip>
    # Download the patch file containing the updated UserSessionManager.java
    wget <patch_file_url>
    # Apply the patch (replace <app_dir> with your application directory)
    patch <app_dir>/src/main/java/com/example/UserSessionManager.java <patch_file>
    # Rebuild and redeploy the application
    mvn clean install
    sudo systemctl restart appserver
    ```

4. **Add Monitoring and Alerts:**
    ```bash
    # Install and configure monitoring tool (e.g., Prometheus, Zabbix)
    # Configure memory usage metrics for the application server
    # Set up alerts to trigger when memory utilization reaches 80%
    # Configure alert notifications (e.g., email, Slack)
    ```

5. **Create Load Balancing Configuration:**
    ```bash
    # Provision a new application server instance and configure it identically to the existing one.
    # Configure load balancer (e.g., HAProxy, Nginx) to distribute traffic between the two application server instances.
    # Verify load balancer functionality.
    ```

## Verification Procedures

* After each step, monitor server resource utilization (CPU, memory) using monitoring tools or system commands.
* Simulate user load using load testing tools (e.g., JMeter, Gatling) to verify stability and performance under expected and peak loads.
* Check application server logs for any errors or exceptions.
* Verify application functionality after each change.

## Rollback Instructions

* **Step 1 & 2:** Revert configuration changes in `/etc/appserver/config.xml` and web server configuration file. Restart respective services.
* **Step 3:** Redeploy the previous version of the application.
* **Step 4:** Disable the newly configured monitoring and alerts.
* **Step 5:** Remove the newly added application server instance and revert load balancer configuration.

## Troubleshooting

* **"Out of Memory" errors persist:**  Verify the JVM heap size increase was applied correctly. Check for other potential memory leaks.
* **Application performance is still slow:** Investigate database performance, network latency, or other bottlenecks.
* **Load balancer issues:** Verify load balancer configuration and connectivity between load balancer and application servers.
* **Patch application issues:**  Revert the patch and contact the development team for further troubleshooting.


This runbook provides a structured approach to resolve the application server crash issue.  Careful implementation and thorough verification are crucial for success.  Ensure all changes are documented and communicated effectively.
