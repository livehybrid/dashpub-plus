#export DOCKER_DEFAULT_PLATFORM=linux/amd64
export BUILD_IMAGES=${BUILD_IMAGES:-false};
export DOCKER_COMPOSE_BUILD_OPTION=$([ "$BUILD_IMAGES" = "true" ] && echo "--file docker-compose-build.yml up -d --build" || echo "up -d");
export DASHPUB_ARCH=${DASHPUB_ARCH:-"main"};
export DASHPUB_ARCH_FILENAME="-$DASHPUB_ARCH"
touch .tokenenv
docker compose --env-file .tokenenv --file docker-compose-splunk.yml up -d --remove-orphans
until docker compose --file docker-compose-splunk.yml logs splunk | grep "Ansible playbook complete"; do
    echo .
    sleep 5
done
export SPLUNK_URL=$(docker compose --file docker-compose-splunk.yml port splunk 8089)

echo $SPLUNK_URL
export SPLUNK_USERNAME=admin
python3 setup-auth.py
set +e
set +x
docker compose --env-file .tokenenv --file docker-compose$DASHPUB_ARCH_FILENAME.yml --file docker-compose-splunk.yml $DOCKER_COMPOSE_BUILD_OPTION
echo "Waiting for Dashpub to build"
until docker compose --file docker-compose-splunk.yml --file docker-compose$DASHPUB_ARCH_FILENAME.yml logs dashpub | grep "started server"; do
    echo .
    sleep 15
done

WEBPORT=$(docker compose --file docker-compose$DASHPUB_ARCH_FILENAME.yml port $( [ "$DASHPUB_ARCH" = "simple" ] || [ "$DASHPUB_ARCH" = "dev" ] && echo "dashpub 3000" || echo "nginx 3001" ))
echo "Access Dashpub at http://$WEBPORT"