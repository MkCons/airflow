from airflow import DAG
from airflow.decorators import task
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import timedelta
import logging
import requests
import pendulum


# inits
DB = "cat_covid"
METADATA_NAME = "metadata"
COLLECTION = 'regio_sexe_edat'
doc = 'https://analisi.transparenciacatalunya.cat/Salut/Registre-de-casos-de-COVID-19-a-Catalunya-per-regi/qwj8-xpvk'
data_url = "https://analisi.transparenciacatalunya.cat/resource/qwj8-xpvk.json?"
offset = 0
limit = 100000
order = 'data'

# logger
log = logging.getLogger(__name__)

# dag
with DAG(
    dag_id='covid_regio_sexe_edat',
    schedule_interval='00 10 * * *',
    start_date=pendulum.datetime(2022, 4, 2, tz="Europe/Madrid"),
    catchup=False,
    tags=['covid'],
    default_args={
        'retries': 5,
        'retry_delay': timedelta(hours=1),
    }
) as dag:
    @task(task_id="update_dataset")
    def update_dataset():
        global offset
        updated_records = 0
        mongo = MongoHook(conn_id="MongoURV")
        metadata = mongo.get_collection(METADATA_NAME, DB)
        data = mongo.get_collection(COLLECTION, DB)
        previous_execution = metadata.find_one({'collection': COLLECTION}, {'num_records': 1})
        if previous_execution is not None:
            offset = previous_execution['num_records']

        while True:
            query = {'$offset': offset, '$limit': limit, '$order': order}
            response = requests.get(data_url, params=query)
            if not response.ok:
                raise Exception('Failed request: ' + response)

            response = response.json()
            if len(response) > 0:
                data.insert_many(response)
            else:
                raise Exception('No new data found')

            offset += len(response)
            updated_records += len(response)

            if len(response) < limit:
                res = metadata.update_one({'collection': COLLECTION},
                                          {'$set': {'num_records': offset,
                                                    'url': doc}}, upsert=True)
                if res is None:
                    raise Exception('Failed metadata insert')
                break
        mongo.close_conn()

        return 'Records updated: ' + str(updated_records)

    run_this = update_dataset()

    run_this

