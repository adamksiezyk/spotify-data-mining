import pendulum
from airflow.models import Variable

DEFAULT_DAG_ARGS = {
    "start_date": pendulum.now(tz="UTC"),
}

# The Variable.get() method has to beused, because templates are rendered at task runtime
APP_MOUNT = Variable.get("spotify_app_mount")

APP_ENV = {
    'DB_TYPE': "{{ conn.spotify_db.conn_type }}",
    'DB_ADDRESS': "{{ conn.spotify_db.host }}",
    'DB_PORT': "{{ conn.spotify_db.port }}",
    'DB_NAME': "{{ conn.spotify_db.schema }}",
    'DB_USERNAME': "{{ conn.spotify_db.login }}",
    'DB_PASSWORD': "{{ conn.spotify_db.password }}",
    'CLIENT_ID': "{{ conn.spotify_api.login }}",
    'CLIENT_SECRET': "{{ conn.spotify_api.password }}",
    'DATA_PATH': APP_MOUNT
}
