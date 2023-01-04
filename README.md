# Spotify data analysis

## App setup

### Create a Spotify app

To communicate with the Spotify API an app has to be created.
Follow the instructions at:
<a href="https://developer.spotify.com/dashboard/applications">Spotify Apps Dashboard</a>.

### Save the Spotify app credentials

Add the `CLIENT_ID` and `CLIENT_SECRET` values to the `.env` file.
They can be obtained from the Spotify app created in the previous step.

### Create and initialize the database, container network and volume

```
docker-compose up
```

## Airflow setup

### Setting the right Airflow user

```
cd airflow
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

### Initialize the database

```
docker-compose up airflow-init
```

### Running Airflow

```
docker-compose up
```

### Oper Airflow UI

Open <a href="http://localhost:8080">Airflow</a>. The default login is `airflow` and default password `airflow`.

### Setup the required Variables and Connections

Create the following Variables:
* `spotify_app_mount` - the docker volue mount point in the task container.
```
/data
```

Create the dollowing connections:
* `spotify_db` - the DB credentials:
    * Type: Postgres
    * Host: db
    * Schema: spotify
    * Login: spotify
    * Password: spotify
    * Port: 5432
* `spotify_api` - the Spotify app credentials:
    * Type: HTTP
    * Host: https://accounts.spotify.com
    * Login: <CLIENT_ID>
    * Password: <CLIENT_SECRET>

## Process new charts

To process new charts, copy them to the `/data` directory and run the `data-collection` DAG.
