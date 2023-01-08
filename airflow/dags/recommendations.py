from airflow import DAG

from utils import DEFAULT_DAG_ARGS
from operators import Operator

with DAG(dag_id="recommendations",
         tags=["spotify"],
         default_args=DEFAULT_DAG_ARGS) as dag:
    t_create_df_with_popularity = Operator(task_id="create_df_with_popularity",
                                           cmd=["python3", "scripts/create_df_with_popularity.py"])

    t_create_recommendations = Operator(task_id="create_recommendations",
                                        cmd=["python3", "scripts/create_recommendation.py"])

    t_create_recommendations_cluster = Operator(task_id="create_recommendations",
                                        cmd=["python3", "scripts/create_recommendation_cluster.py"])

    t_create_df_with_popularity >> [t_create_recommendations, t_create_recommendations_cluster]