# Dashpub Plus Documentation

## Introduction

Dashpub Plus aims to enhance the existing Dashpub project by providing better segregation between Splunk and the end-users, allowing for higher scaling capabilities and improved performance. The primary driver behind this is to improve security by separating from Splunk and by reducing running costs, utilizing a Redis Cache for search results to ensure that multiple searches are not run against Splunk unnecessarily. This ensures that if multiple users visit a dashboard simultaneously, the number of searches run against Splunk is minimized.

## Components

Dashpub Plus "out of the box" consists of the following components:

- **Dashpub**: The main web application serving dashboards.
- **Cache API**: A RESTful API to interact with Redis and Dashpub.
- **Nginx**: Used to distribute traffic between Dashpub (for static content) and the Cache API for `/api` traffic which consists of search results.
- **Redis**: A single node or Redis cluster with 3 nodes for caching search results.
- **Splunk Enterprise**: Standalone Splunk instance, including one example dashboard for demonstration purposes.

## Architecture

### Overview

The architecture of Dashpub Plus is designed to optimize performance and security by using a caching layer and segregating different types of traffic. Here’s a high-level overview of how the components interact:

1. **Nginx**: Acts as the reverse proxy and load balancer.

   - Routes static content requests to Dashpub.
   - Routes API requests to the Cache API.

2. **Dashpub**: Serves the static content (dashboards) to the end-users and performs searches on behalf of the Cache API.

3. **Cache API**: Interacts with the Redis cache to fetch or store search results.

   - When a search request is made, the Cache API checks Redis for cached results.
   - If results are not cached, the Cache API queries Splunk, caches the results, and returns them to the requester.
   - If two people simultaenous request a result, the second request will wait for the results from the first requestor rather than also searching.

4. **Redis Cache**: Stores cached search results to reduce load on Splunk and provide better segregation.

5. **Splunk Enterprise**: Data source for your results.

### Diagram

![Architecture Diagram](images/architecture_diagram.png)

## Installation

### Prerequisites

- Docker and Docker Compose installed on the host machine. (Tested on Linux & Mac Silicon)

### Steps; easy as 1,2,3

1. **Clone the Repository**

   ```bash
   git clone https://github.com/livehybrid/dashpub-plus.git
   cd dashpub-plus
   ```

2. **Customise**
   Whilst the demo environment will work out the box, you may wish to modify `docker-compose-main.yml` to connect to an external Splunk instance and pull in your own dashboards. For more information on Dashpub's environment variables please see [Dashpub's Docker Docs](https://github.com/livehybrid/dashpub/blob/master/docker/README.md).

3. **Start the Services**
   Simply run setup.sh - this process will configure an authentication token for Splunk and then start the rest of the services, providing you a link to your dashboard(s).

## Docker Compose Files

### Main Docker Compose File

Coming soon

### Splunk Docker Compose File

Coming soon

### Build Compose File

Coming soon

## Docker Compose Variables

Here is a table of the necessary environment variables:

| Variable        | Description                     |
| --------------- | ------------------------------- |
| `REDIS_HOST`    | Hostname of the Redis server    |
| `REDIS_PASS`    | Password for Redis              |
| `REDIS_USER`    | Username for Redis              |
| `SPLUNKD_HOST`  | Hostname of the Splunk server   |
| `SPLUNKD_PORT`  | Port for Splunk server          |
| `SPLUNKD_USER`  | Username for Splunk             |
| `SPLUNKD_TOKEN` | Authentication token for Splunk |

**Note**: It is not the aim of this project to help users manage credentials. These are managed in environment variables.

## Setup and Configuration

The process is designed to be as easy as possible. The minimum requirements are to have Docker on Linux. The user can then run the `setup-splunk.sh` script, which will create a Splunk container, generate an authentication token once it has finished booting, and provide dashboards for the example use case/demo. The necessary minimum environment variables have already been set for Redis, Splunk, and Dashpub.

## Monitoring and Logging

The code is not currently instrumented for monitoring. However, using Docker, it is possible to specify logging output to Splunk HEC depending on the user's requirements. Here is an example of the config which could be applied to the nginx container to send logs to Splunk:

```yaml
logging:
  driver: splunk
  options:
    splunk-format: raw
    splunk-index: nginx_web
    splunk-source: docker:dashpub:nginx
    splunk-sourcetype: nginx:plus:access
    splunk-token: <YourHECToken>
    splunk-url: <YourSplunkHECEndpoint>
    splunk-verify-connection: false
```

For more information see the [Docker logging driver docs](https://docs.docker.com/config/containers/logging/splunk/)

## Advanced Configuration options

Coming soon

## Advanced Architectures

Coming soon

## Scaling and Performance

To handle increased load, users could place Redis clusters across multiple servers. Depending on the situation, it may be more appropriate to extend this architecture further, such as fronting the service with AWS CloudFront and then using Elasticache Redis for the cache. Docker containers could be scaled horizontally for high availability and improved fault tolerance.

## Troubleshooting

### Possible Issues

- **Connectivity Problems**: Check network configurations and ensure all docker services are running (`docker ps -a`).
- ** No Search results on Dashboards**: Verify the Splunk credentials and tokens. If using demo configuration then ensure that setup.sh reported successfully retrieving the token from Splunk.

### Steps to Troubleshoot

1. **Review Logs**: Check logs for each docker service / component to identify any errors or issues, feel free to raise an issue in GitHub providing as much detail as possible.
2. **Check Environment Variables**: Ensure all required environment variables are correctly set.
3. **Raise an Issue**: If the problem persists, raise an issue on the [GitHub repository](https://github.com/livehybrid/dashpub-plus/issues).

## Questions and Answers

Coming Soon

## Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](https://github.com/livehybrid/dashpub-plus/blob/main/CONTRIBUTING.md) file for more details.

## Contact

For further questions or support, please open an issue on the [GitHub repository](https://github.com/livehybrid/dashpub-plus/issues).
