export DOCKER_DEFAULT_PLATFORM=linux/amd64

touch .tokenenv
docker compose --env-file .tokenenv --file docker-compose-splunk.yml up -d
until docker compose --file docker-compose-splunk.yml logs splunk | grep "Ansible playbook complete"; do
    echo -n .
    sleep 1
done
export SPLUNK_URL=$(docker compose port splunk 8089)

echo $SPLUNK_URL
export SPLUNK_USERNAME=admin
python3 setup-auth.py
docker compose --env-file .tokenenv --file docker-compose.yml --file docker-compose-splunk.yml up -d