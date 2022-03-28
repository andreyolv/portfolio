# [START pre_requisites]
# pip install apache-airflow-providers-amazon
# [END pre_requisites]
# --------------------------------------------------------------------------------------------------------
# [START documentation]
"""
https://registry.astronomer.io/providers/amazon/modules/s3createbucketoperator
https://registry.astronomer.io/providers/amazon/modules/localfilesystemtos3operator
https://registry.astronomer.io/providers/amazon/modules/s3keysensor
https://registry.astronomer.io/providers/amazon/modules/s3listoperator
https://registry.astronomer.io/providers/amazon/modules/s3copyobjectoperator
https://registry.astronomer.io/providers/amazon/modules/s3deleteobjectsoperator
https://registry.astronomer.io/providers/amazon/modules/s3deletebucketoperator
"""
# [END documentation]
# --------------------------------------------------------------------------------------------------------
# [START connections]
"""
Connection Id = s3_minio
Connection Type = Amazon S3
Extra = {"aws_access_key_id": "minioadmin", "aws_secret_access_key": "minioadmin", "host": "http://127.0.0.1:9000"}
"""
# [END connections]
# --------------------------------------------------------------------------------------------------------
# [START import_module]
import pandas as pd
from minio import Minio
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.providers.amazon.aws.operators.s3_list import S3ListOperator
from airflow.providers.amazon.aws.operators.s3_copy_object import S3CopyObjectOperator
from airflow.providers.amazon.aws.operators.s3_delete_objects import S3DeleteObjectsOperator
from airflow.providers.amazon.aws.operators.s3 import S3DeleteBucketOperator
# [END import_module]
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
    'andrey_miniooperator',
    default_args=default_args,
    start_date=datetime(2022, 2, 1),        #(YYYY, MM, DD)
    schedule_interval="@monthly",           #@monthly = "0 0 1 * *"
    tags=['raizen2', 'oportunidade2', 'uhull']
)
# [END instantiate_dag]
# --------------------------------------------------------------------------------------------------------
# [START functions]





# [END functions]
# --------------------------------------------------------------------------------------------------------
# [START set_tasks]
# create a new bucket in landing zone
create_bucket_landing_zone = S3CreateBucketOperator(
    task_id='create_bucket_landing_zone',
    bucket_name='landingzone',
    aws_conn_id='s3_minio',
    dag=dag)

# copy files from local folder to landing zone bucket
copy_localfiles_to_s3 = LocalFilesystemToS3Operator(
    task_id='copy_localfiles_to_s3',
    filename='/home/andreolv/airflow/dags/raw_data/raw_data.xlsx',
    dest_bucket='landingzone',
    dest_key='raw_data.xlsx', 
    replace=True,
    aws_conn_id='s3_minio',
    dag=dag)

# verify if new file has landed into bucket
verify_file_existence_landing = S3KeySensor(
    task_id='verify_file_existence_landing',
    bucket_name='landingzone',
    bucket_key='raw_data.xlsx',
    aws_conn_id='s3_minio',
    poke_interval=60, # a cada quantos segundos ele vai tentar verificar se o arquivo existe
    timeout=60*10,     # vai tentar ler 10 vezes
    dag=dag)

# list all files inside of a bucket [names]
list_file_s3 = S3ListOperator(
    task_id='list_file_s3',
    bucket='landingzone',
    delimiter='/',
    aws_conn_id='s3_minio',
    dag=dag)

# create a new bucket of processing zone
create_bucket_processing_zone = S3CreateBucketOperator(
    task_id='create_bucket_processing_zone',
    bucket_name='processingzone',
    aws_conn_id='s3_minio',
    dag=dag)   

# copy file from landing to processing zone
copy_s3_file_processed_zone = S3CopyObjectOperator(
    task_id='copy_s3_file_processed_zone',
    source_bucket_name='landingzone',
    source_bucket_key='/raw_data.xlsx',
    dest_bucket_name='processingzone',
    dest_bucket_key='/raw_data.xlsx',
    aws_conn_id='s3_minio',
    trigger_rule="all_success",
    dag=dag)

# delete file from landing zone [old file]
delete_s3_file_landing_zone = S3DeleteObjectsOperator(
    task_id='delete_s3_file_landing_zone',
    bucket='landingzone',
    keys='/raw_data.xlsx',
    aws_conn_id='s3_minio',
    dag=dag)

# delete bucket landing zone
delete_bucket_landing_zone = S3DeleteBucketOperator(
    task_id='delete_bucket_landing_zone',
    bucket_name='landingzone',
    aws_conn_id='s3_minio',
    dag=dag)

# [END set_tasks]
# --------------------------------------------------------------------------------------------------------
# [START task_sequence] 
create_bucket_landing_zone >> copy_localfiles_to_s3 >> verify_file_existence_landing >> list_file_s3

[list_file_s3, create_bucket_processing_zone] >> copy_s3_file_processed_zone

copy_s3_file_processed_zone >> delete_s3_file_landing_zone >> delete_bucket_landing_zone
# [END task_sequence]
