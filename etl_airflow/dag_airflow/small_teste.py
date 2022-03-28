# https://airflow.apache.org/docs/apache-airflow/stable/start/local.html
# [START import_module]
from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email import EmailOperator   
# from airflow.providers.telegram.operators.telegram import TelegramOperator
# [END import_module]
# --------------------------------------------------------------------------------------------------------
# [START defining variables]
telegram_chat_id = "5151128933"

telegram_token = "AAGOLy3wnyAOI6CRJhlG85d3Jg25RpyLBto"
# [END defining variables]
# --------------------------------------------------------------------------------------------------------
# [START default_args]
default_args = {
    'owner': 'Andrey Olv',
    'depends_on_past': False,
    'email': ['andreyyolv@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1)}
# [END default_args]
# --------------------------------------------------------------------------------------------------------
# [START instantiate_dag]
dag = DAG(
    'andrey_pipeline_teste',
    default_args=default_args,
    start_date=datetime(2022, 1, 1),
    schedule_interval="@monthly",   #@monthly = "0 0 1 * *"
    tags=['raizen', 'oportunidade', 'uhull']
)
# [END instantiate_dag]
# --------------------------------------------------------------------------------------------------------
# [START basic_task]
postgres2 = PostgresOperator(
    task_id='load_postgres_postgresoperator',
    postgres_conn_id='andrey_postgres_localhost',
    sql='''
        CREATE TABLE raw_data_postgresql (
            id SERIAL PRIMARY KEY,
            year_month DATE NOT NULL,
            uf VARCHAR(20) NOT NULL,
            product VARCHAR(40) NOT NULL,
            unit CHAR(2) NOT NULL,
            volume DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP NOT NULL);
        ''',
    dag=dag)

send_message_email = EmailOperator(
    task_id='send_email',
    to="andreyyolv@gmail.com",
    subject="[AIRFLOW] Pipeline Raizen Completed",
    html_content="<h3>Congratulations Andrey! Your pipeline was successful completed!</h3>",
    trigger_rule="all_success",
    dag=dag)
# [END basic_task]
# --------------------------------------------------------------------------------------------------------
# [START task_sequence]
# [END task_sequence]