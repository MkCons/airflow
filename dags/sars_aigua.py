from airflow import DAG
from airflow.decorators import task
from airflow.providers.mongo.hooks.mongo import MongoHook
import logging
import pendulum

# inits
DB = "cat_covid"
METADATA_NAME = "metadata"
COLLECTION_NAME = 'sars_aigues'
doc = ['https://zenodo.org/record/6390012', 'https://github.com/icra/sars-aigues/']

data_url = 'https://raw.githubusercontent.com/icra/sars-aigues/main/release_with_detection_limits.csv'


# logger
log = logging.getLogger(__name__)

# dag
with DAG(
    dag_id='sars_aigua',
    schedule_interval='00 11 * * *',
    start_date=pendulum.datetime(2022, 4, 2, tz="Europe/Madrid"),
    catchup=False,
    tags=['covid'],
    default_args={
        'retries': 0,
    }
) as dag:
    @task(task_id="update_dataset")
    def update_dataset():
        import pandas as pd  # best practice
        import json

        # client = MongoClient('localhost', 27017, username='****', password='****')
        mongo = MongoHook(conn_id="MongoURV")
        client = mongo.get_conn()

        database = client[DB]
        data = database[COLLECTION_NAME]
        metadata = database[METADATA_NAME]

        num_records = 0
        previous_execution = metadata.find_one({'collection': COLLECTION_NAME}, {'num_records': 1})
        if previous_execution is not None:
            num_records = previous_execution['num_records']

        # get data
        df = pd.read_csv(data_url, encoding='utf-8')
        response = df.to_json(orient='records')
        response = response.replace('\\u00da', 'Ú').replace('\\/', '/') \
            .replace('\\u00fa', 'ú').replace('\\u00f2', 'ò').replace('\\u00f3', 'ó').replace('\\u00c8', 'È') \
            .replace('\\u00e8', 'è').replace('\\u00c0', 'À').replace('\\u00c9', 'É').replace('\\u00e9', 'é') \
            .replace('\\u00cd', 'Í').replace('\\u00fc', 'ü').replace('\\u00d3', 'Ó').replace('\\u00e0', 'à') \
            .replace('\\u00d2', 'Ó').replace('\\u00ed', 'í')

        response = json.loads(response)

        if len(response) > num_records:
            num_records = len(response)
            data.drop()
            data.insert_many(response)
            res = metadata.update_one({'collection': COLLECTION_NAME}, {'$set': {'num_records': num_records,
                                                                                 'url': doc}}, upsert=True)
            if res is None:
                raise Exception('Failed metadata insert')
        else:
            raise Exception('No new data found')

        client.close()
        return 'Records updated: ' + str(num_records)

    run_this = update_dataset()

    run_this
