from airflow import DAG
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import logging
from pprint import pprint
from airflow.decorators import task
import logging
import shutil
import time
from pprint import pprint

import pendulum

from airflow import DAG
from airflow.decorators import task

log = logging.getLogger(__name__)

with DAG(
    dag_id='simple-mongo-test',
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=['example'],
) as dag:
    # @task(task_id="test_context")
    def test_context():
        print('hello world')
        mongoHook = MongoHook(conn_id="MongoURV")
        result = mongoHook.insert_one(mongo_collection="test-col", doc={"test": 1234})
        print(result.acknowledged)
        print(result.inserted_id)
        mongoHook.close_conn()
        return 'Whatever you return gets printed in the logs'

    run_this = test_context()

    run_this
