from airflow import DAG
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import logging
from pprint import pprint
from airflow.decorators import task


log = logging.getLogger(__name__)


def test():
    mongoHook = MongoHook(conn_id="MongoURV")
    mongoHook.insert_one(mongo_collection="test-col", doc={"test": 1234})

    collection = mongoHook.get_collection("collection_name2", "cat-covid")
    result = collection.insert_one({"test": 1234})
    log.warning(result)
    mongoHook.close_conn()


with DAG(dag_id='mongo-test',
    default_args={
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1
    },
    description='testing',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 4, 1),
    catchup=False,
    tags=['example'],
) as dag:

    @task(task_id="print_the_context")
    def print_context(ds=None, **kwargs):
        """Print the Airflow context and ds variable from the context."""
        pprint(kwargs)
        print(ds)
        return 'Whatever you return gets printed in the logs'

    run_this = print_context()

    t1 = PythonOperator(task_id="update",
                        python_callable=test)

    t1

