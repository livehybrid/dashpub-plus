#export DOCKER_DEFAULT_PLATFORM=linux/amd64
export BUILD_IMAGES=${BUILD_IMAGES:-false}
export DOCKER_COMPOSE_BUILD_OPTION=$([ "$BUILD_IMAGES" = "true" ] && echo "--file docker-compose-build.yml up -d --build" || echo "up -d")

export DASHPUB_ARCH=${DASHPUB_ARCH:-"main"}
export DASHPUB_ARCH_FILENAME="-$DASHPUB_ARCH"
export SPLUNKD_URL=${SPLUNKD_URL:-"https://splunk:8089"}

# Include the Splunk file if using the docker splunk instance, else do not.
DOCKER_COMPOSE_SPLUNKFILE=$([ "$SPLUNKD_URL" = "https://splunk:8089" ] && echo "--file docker-compose-splunk.yml" || echo "")

touch .tokenenv

if [ "$SPLUNKD_URL" = "https://splunk:8089" ]; then
    echo "Starting local Splunk container"
    docker compose --env-file .tokenenv --file docker-compose-splunk.yml up -d --remove-orphans
    until docker compose --file docker-compose-splunk.yml logs splunk | grep "Ansible playbook complete"; do
        echo .
        sleep 5
    done
    export SPLUNKD_URL=https://$(docker compose --file docker-compose-splunk.yml port splunk 8089)
    export SPLUNKD_USERNAME=admin
else 
    echo "Not starting Splunk docker container as using external instance: $SPLUNKD_URL"
fi

if [ -z "$SPLUNKD_TOKEN" ]; then
    echo "No SPLUNKD_TOKEN variable set so creating using SPLUNKD_USERNAME and SPLUNKD_PASSWORD variables against $SPLUNKD_URL"
    python3 setup-auth.py
fi

docker compose --env-file .tokenenv --file docker-compose$DASHPUB_ARCH_FILENAME.yml $DOCKER_COMPOSE_SPLUNKFILE $DOCKER_COMPOSE_BUILD_OPTION
echo "Waiting for Dashpub to build - this takes 2-3 minutes"
until docker compose $DOCKER_COMPOSE_SPLUNKFILE --file docker-compose$DASHPUB_ARCH_FILENAME.yml logs dashpub | grep "started server"; do
    echo .
    sleep 15
done

if [ "$DASHPUB_ARCH" = "simple" ] || [ "$DASHPUB_ARCH" = "dev" ]; then
    WEBPORT=$(docker compose --file docker-compose$DASHPUB_ARCH_FILENAME.yml port dashpub 3000)
else
    docker compose --file docker-compose$DASHPUB_ARCH_FILENAME.yml $DOCKER_COMPOSE_SPLUNKFILE restart nginx
    WEBPORT=$(docker compose --file docker-compose$DASHPUB_ARCH_FILENAME.yml port nginx 3001)
    
    echo "Restarting screenshotter to capture initial image"
    docker compose --file docker-compose$DASHPUB_ARCH_FILENAME.yml $DOCKER_COMPOSE_SPLUNKFILE restart screenshotter
fi
echo "Access Dashpub at http://$WEBPORT"

