# Runbook: Resolve Application Server (Tomcat 9) Crashes Under High Load

## Executive Summary

This runbook outlines the procedures to address "Application Server Crashes Under High Load" for Tomcat 9. The root cause has been identified as a memory leak in user session handling introduced in the latest feature update (v1.2.3). This runbook prioritizes fixing the memory leak, implementing robust monitoring and alerting, and optimizing resource allocation based on load testing. It also includes steps for load balancing and connection throttling as secondary measures to ensure long-term stability and scalability.

## Detailed Issue Description and Impact

The Tomcat 9 web application server experiences crashes when the number of concurrent users exceeds 500. The crashes are preceded by "Out of Memory" errors logged in the server logs (`/var/log/tomcat9/catalina.out`). This issue emerged following the deployment of the feature update v1.2.3. The crashes severely impact application availability and user experience, leading to service disruption and potential business losses.

## Prerequisites

* **Access:** SSH access to the application server with root privileges.
* **Tools:** JDK 8, Maven 3, JProfiler, JMeter.
* **Credentials:** Access credentials for the Datadog monitoring system and HAProxy load balancer.
* **Files:** Patched `UserSessionManager.java` file (v1.2.4).
* **Backup:** A recent backup of the Tomcat server configuration (`/etc/tomcat9`) and application files (`/var/lib/tomcat9/webapps`).

## Step-by-Step Implementation Instructions

### 1. Fix Memory Leak in User Session Handling

1.1. **Deploy Patched File:**
    * Compile the patched `UserSessionManager.java` (v1.2.4) using Maven: `mvn clean compile`
    * Copy the compiled `.class` file to the Tomcat web application directory: `cp target/classes/com/example/app/UserSessionManager.class /var/lib/tomcat9/webapps/myapp/WEB-INF/classes/com/example/app/`
    * Commit the change to version control: `git add /path/to/UserSessionManager.java && git commit -m "Fix: Memory leak in UserSessionManager (v1.2.4)"`

1.2. **Restart Application Server:** `systemctl restart tomcat9`

1.3. **Verify Patch Deployment:** `md5sum /var/lib/tomcat9/webapps/myapp/WEB-INF/classes/com/example/app/UserSessionManager.class` and compare the checksum with the known checksum of the v1.2.4 `UserSessionManager.class` file.

### 2. Implement Robust Monitoring and Alerting (Datadog)

2.1. **Install/Configure Monitoring Agent:** Install the Datadog agent using the instructions provided in the Datadog documentation for Tomcat 9.  Configure the agent to connect to your Datadog account.

2.2. **Configure Memory Monitoring:** Configure the Datadog agent to monitor JVM heap memory usage, CPU utilization, request latency, and error rates.  Use the Datadog Java integration for detailed JVM metrics.

2.3. **Set Up Alerts:** Create Datadog monitors to trigger email and Slack notifications when heap memory usage exceeds 70% and 85%.  Set alerts for unusual spikes in CPU utilization (above 90%), request latency (above 500ms), and error rates (above 1%).

2.4. **Test Alerts:** Use JMeter to generate load and push memory usage past the threshold. Manually trigger an error condition in the application to test error rate alerts.

### 3. Increase Server Memory Allocation (Carefully)

3.1. **Conduct Load Testing:**  Perform load testing with JMeter, simulating 750 concurrent users with a mix of read and write requests for 30 minutes.

3.2. **Adjust JVM Heap Size:**  Based on the load test results, adjust the JVM heap size in `/etc/tomcat9/bin/setenv.sh`:  `export CATALINA_OPTS="$CATALINA_OPTS -Xmx4g -Xms2g"` (This sets the maximum heap size to 4GB and the initial heap size to 2GB.  Be aware of potential garbage collection issues with very large heap sizes.)

3.3. **Restart Application Server:** `systemctl restart tomcat9`

### 4. Implement Load Balancing (HAProxy)

4.1. **Provision New Server Instance:** Set up an additional Tomcat 9 server instance, configured identically to the existing one.

4.2. **Configure Load Balancer:** Configure HAProxy to distribute incoming traffic using the round-robin algorithm across both Tomcat instances. Configure session persistence using sticky sessions. Refer to HAProxy documentation for specific configuration examples.

4.3. **Test Load Balancing:** Generate test traffic with JMeter and verify traffic distribution and application functionality on both instances.

### 5. Consider Connection Throttling (HAProxy)

5.1. **Configure Throttling:** Configure connection throttling in HAProxy.  Limit the number of concurrent connections to 1000 per backend server.  Example:  `maxconn 1000`.

5.2. **Implement Request Queuing:** Configure HAProxy to queue excess requests when the connection limit is reached. Example: `tune.bufsize 262144`.

5.3. **Test and Tune:** Test the throttling and queuing mechanisms under high load and adjust limits as needed to balance performance and user experience.


## Verification Procedures

* **Monitor Resource Usage:**  Monitor server resource utilization (memory, CPU) using Datadog under typical and high load conditions (JMeter) to ensure stability.
* **Application Functionality Testing:** Perform comprehensive testing of the application's core functionality, especially user session management, under various load levels.
* **Alert Verification:** Verify that Datadog alerts are triggered appropriately during load testing.
* **Check Application Logs:** Review Tomcat logs (`/var/log/tomcat9/catalina.out`) for any error messages related to memory or performance.

## Rollback Instructions

1. **Revert `UserSessionManager.java`:**  `git revert <commit-hash>` of the v1.2.4 commit.
2. **Revert Memory Settings:** Remove or comment out the `CATALINA_OPTS` settings in `/etc/tomcat9/bin/setenv.sh`.
3. **Restart Application Server:** `systemctl restart tomcat9`
4. **Disable Load Balancing/Throttling:**  Revert HAProxy configuration to disable load balancing and connection throttling.

## Troubleshooting

| Issue | Possible Cause | Solution |
|---|---|---|
| Application still crashes after patching `UserSessionManager.java` | Incomplete fix of the memory leak | Re-examine the patch, conduct further testing and profiling with JProfiler. |
| Performance degradation after increasing memory allocation | Excessive memory allocation leading to inefficient garbage collection | Reduce the allocated memory based on load testing results. Analyze GC logs. |
| Load balancer not distributing traffic evenly | Incorrect load balancer configuration | Verify HAProxy settings and server health checks. |
| Increased latency after implementing connection throttling | Throttling limits too restrictive | Adjust throttling limits in HAProxy based on performance testing and user experience considerations. |
| Application performance is slow after patch | Inefficient code in the patch | Profile the patched code with JProfiler, optimize performance. |
| Monitoring alerts are not being sent | Monitoring agent misconfigured | Check Datadog agent logs, verify connection to Datadog and notification systems. |
| Load balancer is unavailable | Network issues, server failure | Check network connectivity, restart HAProxy server. |


This runbook provides a structured approach to resolving the Tomcat 9 application server crashes. By addressing the root cause and implementing proactive monitoring and scaling solutions, it aims to ensure long-term application stability and a positive user experience.
