from airflow import DAG

from utils import DEFAULT_DAG_ARGS
from operators import Operator


with DAG(dag_id="data-collection",
         tags=["spotify"],
         default_args=DEFAULT_DAG_ARGS) as dag:
    t_create_db = Operator(task_id="create_db", cmd=["python3", "scripts/create_db.py"])

    t_create_charts = Operator(task_id="create_charts", cmd=["python3", "scripts/create_charts.py"])

    t_create_charts_statistics = Operator(task_id="create_charts_statistics",
                                          cmd=["python3", "scripts/create_charts_statistics.py"])

    t_create_db >> t_create_charts >> t_create_charts_statistics
