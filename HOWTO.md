First, checkout https://github.com/apache/airflow
Update python version, add mongo extra to Dockerfile
Then build the image

docker build . -f Dockerfile --pull --tag airflow-urv:0.0.1

Then https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html

mkdir -p ./dags ./logs ./plugins ./keys
echo -e "AIRFLOW_UID=$(id -u)" > .env

# get the compose file and modify the image it references
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.2.4/docker-compose.yaml'

# start the db
docker-compose up airflow-init

# start airflow
docker-compose up

# generate keys
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# remove all
docker-compose down --volumes --rmi all
