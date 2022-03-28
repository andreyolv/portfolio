# https://airflow.apache.org/docs/apache-airflow/stable/start/local.html
# [START import_module]
from re import T
from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email import EmailOperator   
from airflow.providers.telegram.operators.telegram import TelegramOperator
from sqlalchemy import create_engine
import time
import pandas as pd
import numpy as np
import os, os.path
# [END import_module]
# --------------------------------------------------------------------------------------------------------
# [START defining variables]
path_file = '/home/andreolv/airflow/dags/'

month_map = {'Jan':'01', 'Fev':'02', 'Mar':'03', 'Abr': '04', 'Mai':'05', 'Jun':'06',
            'Jul':'07', 'Ago':'08', 'Set':'09', 'Out':'10', 'Nov':'11', 'Dez':'12',
            'COMBUSTÍVEL':'product', 'ESTADO': 'uf'}

estados = ['ACRE', 'ALAGOAS', 'AMAPÁ', 'AMAZONAS', 'BAHIA', 'CEARÁ', 'DISTRITO FEDERAL', 'ESPÍRITO SANTO',
            'GOIÁS', 'MARANHÃO', 'MATO GROSSO', 'MATO GROSSO DO SUL', 'MINAS GERAIS', 'PARÁ', 'PARAÍBA', 
            'PARANÁ', 'PERNAMBUCO', 'PIAUÍ', 'RIO DE JANEIRO', 'RIO GRANDE DO NORTE', 'RIO GRANDE DO SUL',
            'RONDÔNIA', 'RORAIMA', 'SANTA CATARINA', 'SÃO PAULO', 'SERGIPE', 'TOCANTINS']

produtos = ['ETANOL HIDRATADO', 'GASOLINA C', 'GASOLINA DE AVIAÇÃO', 'GLP', 
            'ÓLEO COMBUSTÍVEL', 'ÓLEO DIESEL', 'QUEROSENE DE AVIAÇÃO', 
            'QUEROSENE ILUMINANTE', 'ÓLEO DIESEL (OUTROS )', 'ÓLEO DIESEL MARÍTIMO', 
            'ÓLEO DIESEL S-10', 'ÓLEO DIESEL S-1800', 'ÓLEO DIESEL S-500']

anos = [str(x) for x in list(range(2000,2021))]

column_names_ordered = ["year_month", "uf", "product", "unit", "volume", "created_at"]

telegram_chat_id = "5151128933"

telegram_token = "AAGOLy3wnyAOI6CRJhlG85d3Jg25RpyLBto"

# [END defining variables]
# --------------------------------------------------------------------------------------------------------
# [START python functions]
# Funções para as DAGs da Tabela 1
def extract_table_1():
    df1 = pd.read_excel(path_file+'raw_file/vendas-combustiveis-m3.xlsx', sheet_name='DPCache_m3')
    df1.to_excel(path_file+'temp_data/df1.xlsx', index=False)

def transform_table_1():
    df2 = pd.read_excel(path_file+'temp_data/df1.xlsx')
    # Converte o nome das colunas do dataframe
    df2.rename(columns = month_map, inplace = True)
    df2.to_excel(path_file+'temp_data/df2.xlsx', index=False)

def transform_table_2():
    df3 = pd.read_excel(path_file+'temp_data/df2.xlsx')
    # Remove as colunas que não são necessárias
    df3 = df3.drop(['REGIÃO', 'TOTAL'], axis=1)
    df3.to_excel(path_file+'temp_data/df3.xlsx', index=False)

def transform_table_3():
    df4 = pd.read_excel(path_file+'temp_data/df3.xlsx')
    # Pivoteia as colunas dos meses para linhas
    df4 = pd.melt(df4, id_vars=["product", "ANO", "uf"], var_name="MES", value_name='volume')
    df4.to_excel(path_file+'temp_data/df4.xlsx', index=False)

def transform_table_4():
    df5 = pd.read_excel(path_file+'temp_data/df4.xlsx')
    # Força o tipo da coluna ano para string para facilitar concatenação posterior
    df5 = df5.astype({"ANO":str, "MES":str})
    # Concatena o ano com o mes para formar a coluna year_month
    df5['year_month'] = df5.ANO.str.cat(df5.MES,sep="-")
    # Remove as colunas ano e mes, agora não mais necessárias
    df5 = df5.drop(['ANO', 'MES'], axis=1)
    df5.to_excel(path_file+'temp_data/df5.xlsx', index=False)

def transform_table_5():
    df6 = pd.read_excel(path_file+'temp_data/df5.xlsx')
     # Cria a coluna unit que é sempre igual a 'm3'
    df6['unit'] = "m3"
    # Cria a coluna created_at que é sempre igual ao timestamp atual
    df6['created_at'] = pd.Timestamp.now()
    # Remove a unidade de medida 'm3' do final de cada linha da coluna product
    df6['product'] = df6['product'].str[0:-5]
    # Ordena as colunas do dataframe pela ordem indicada no github do teste
    df6 = df6[column_names_ordered]
    # Remove linhas em que o volume é NaN/vazio pra facilitar a inserção no banco de dados
    df6 = df6.dropna(subset = ['volume'])
    df6.to_excel(path_file+'temp_data/df6.xlsx', index=False)
# --------------------------------------------------
# Funções para as DAGs da Tabela 2
def extract_table_10():
    df10 = pd.read_excel(path_file+'raw_file/vendas-combustiveis-m3.xlsx', sheet_name='DPCache_m3_2')
    df10.to_excel(path_file+'temp_data/df10.xlsx', index=False)

def transform_table_10():
    df20 = pd.read_excel(path_file+'temp_data/df10.xlsx')
    # Converte o nome das colunas do dataframe
    df20.rename(columns = month_map, inplace = True)
    df20.to_excel(path_file+'temp_data/df20.xlsx', index=False)

def transform_table_20():
    df30 = pd.read_excel(path_file+'temp_data/df20.xlsx')
    # Remove as colunas que não são necessárias
    df30 = df30.drop(['REGIÃO', 'TOTAL'], axis=1)
    df30.to_excel(path_file+'temp_data/df30.xlsx', index=False)

def transform_table_30():
    df40 = pd.read_excel(path_file+'temp_data/df30.xlsx')
    # Pivoteia as colunas dos meses para linhas
    df40 = pd.melt(df40, id_vars=["product", "ANO", "uf"], var_name="MES", value_name='volume')
    df40.to_excel(path_file+'temp_data/df40.xlsx', index=False)

def transform_table_40():
    df50 = pd.read_excel(path_file+'temp_data/df40.xlsx')
    # Força o tipo da coluna ano para string para facilitar concatenação posterior
    df50 = df50.astype({"ANO":str, "MES":str})
    # Concatena o ano com o mes para formar a coluna year_month
    df50['year_month'] = df50.ANO.str.cat(df50.MES,sep="-")
    # Remove as colunas ano e mes, agora não mais necessárias
    df50 = df50.drop(['ANO', 'MES'], axis=1)
    df50.to_excel(path_file+'temp_data/df50.xlsx', index=False)

def transform_table_50():
    df60 = pd.read_excel(path_file+'temp_data/df50.xlsx')
     # Cria a coluna unit que é sempre igual a 'm3'
    df60['unit'] = "m3"
    # Cria a coluna created_at que é sempre igual ao timestamp atual
    df60['created_at'] = pd.Timestamp.now()
    # Remove a unidade de medida 'm3' do final de cada linha da coluna product
    df60['product'] = df60['product'].str[0:-5]
    # Ordena as colunas do dataframe pela ordem indicada no github do teste
    df60 = df60[column_names_ordered]
    # Remove linhas em que o volume é NaN/vazio pra facilitar a inserção no banco de dados
    df60 = df60.dropna(subset = ['volume'])
    df60.to_excel(path_file+'temp_data/df60.xlsx', index=False)
# --------------------------------------------------------------------------------------------------------
# Funções para as DAGs da junção e carregamento das tabelas
def concat_tables():
    df7 = pd.read_excel(path_file+'temp_data/df6.xlsx')
    df70 = pd.read_excel(path_file+'temp_data/df60.xlsx')
    # Concatena os dataframes df1 e df2
    concat_data = pd.concat([df7, df70], ignore_index=True)
    
    concat_data.to_excel(path_file+'raw_data/concat_data.xlsx', index=False)

def verify_and_load_excel():
    raw_data = pd.read_excel(path_file+'raw_data/concat_data.xlsx')
    """
    # VERIFICANDO COLUNA 'year_month'
    # Buscando valores na coluna que estão fora no range pre-definido
    bad_data1 = raw_data[~np.isin(raw_data['year_month'].str[0:4], anos)]
    # Removendo estas linhas
    raw_data = raw_data.drop(index=bad_data1.index.tolist())

    # VERIFICANDO COLUNA 'uf'
    # Buscando valores na coluna que estão fora no range pre-definido
    bad_data2 = raw_data[~np.isin(raw_data['uf'], estados)]
    # Removendo estas linhas
    raw_data = raw_data.drop(index=bad_data2.index.tolist())

    # VERIFICANDO COLUNA 'product'
    # Buscando valores na coluna que estão fora no range pre-definido
    bad_data3= raw_data[~np.isin(raw_data['product'], produtos)]
    # Removendo estas linhas
    raw_data = raw_data.drop(index=bad_data3.index.tolist())

    # VERIFICANDO COLUNA 'volume'
    # Buscando valores na coluna que estão fora no range pre-definido
    bad_data4 = raw_data[raw_data['volume'].str.isnumeric() == False]
    # Removendo estas linhas
    raw_data = raw_data.drop(index=bad_data4.index.tolist())
    """
    raw_data.to_excel(path_file+'raw_data/raw_data.xlsx', index=False)

def delete_temp_files():
    lista_arquivos = os.listdir(path_file+'temp_data/')
    for i in lista_arquivos:
        os.remove(path_file+'temp_data/'+i)

def load_postgres_python():
    raw_data2 = pd.read_excel(path_file+'raw_data/raw_data.xlsx')
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    raw_data2.to_sql('raw_data_sqlalchemy', con=engine, if_exists='replace',index=True)

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
    'andrey_pipeline8',
    default_args=default_args,
    start_date=datetime(2022, 2, 1),        #(YYYY, MM, DD)
    schedule_interval="@monthly",           #@monthly = "0 0 1 * *"
    tags=['raizen2', 'oportunidade2', 'uhull']
)
# [END instantiate_dag]
# --------------------------------------------------------------------------------------------------------
# [START basic_task]
is_excel_file_available = FileSensor(
    task_id='is_file_available',
    fs_conn_id="andrey_excel_path",
    filepath="vendas-combustiveis-m3.xlsx",
    poke_interval=60, # a cada quantos segundos ele vai tentar verificar se o arquivo existe
    timeout=60*10     # vai tentar ler 10 vezes
)
# --------------------------------------------
# Tarefas para a tabela 1
e1 = PythonOperator(
    task_id = 'extract_table_1',
    python_callable=extract_table_1,
    dag=dag)

t1 = PythonOperator(
    task_id = 'transform1',
    python_callable=transform_table_1,
    dag=dag)

t2 = PythonOperator(
    task_id = 'transform2',
    python_callable=transform_table_2,
    dag=dag)

t3 = PythonOperator(
    task_id = 'transform3',
    python_callable=transform_table_3,
    dag=dag)

t4 = PythonOperator(
    task_id = 'transform4',
    python_callable=transform_table_4,
    dag=dag)

t5 = PythonOperator(
    task_id = 'transform5',
    python_callable=transform_table_5,
    dag=dag)
# --------------------------------------------
# Tarefas para a tabela 2
e10 = PythonOperator(
    task_id = 'extract_table_2',
    python_callable=extract_table_10,
    dag=dag)

t10 = PythonOperator(
    task_id = 'transform10',
    python_callable=transform_table_10,
    dag=dag)

t20 = PythonOperator(
    task_id = 'transform20',
    python_callable=transform_table_20,
    dag=dag)

t30 = PythonOperator(
    task_id = 'transform30',
    python_callable=transform_table_30,
    dag=dag)

t40 = PythonOperator(
    task_id = 'transform40',
    python_callable=transform_table_40,
    dag=dag)

t50 = PythonOperator(
    task_id = 'transform50',
    python_callable=transform_table_50,
    dag=dag)
# --------------------------------------------
# Tarefa para a junção das tabelas e carregamento
conc = PythonOperator(
    task_id = 'concat_tables',
    python_callable=concat_tables,
    trigger_rule="all_success",
    dag=dag)

verifyload = PythonOperator(
    task_id = 'verify_and_load_excel',
    python_callable=verify_and_load_excel,
    dag=dag)

deletefiles = PythonOperator(
    task_id = 'delete_temp_files',
    python_callable=delete_temp_files,
    dag=dag)
# --------------------------------------------
# Tarefa para transferrir dados para Postgres via PostgresOperator
# Cria a Tabela raw_data_postgresoperator
table1_postgres = PostgresOperator(
    task_id='create_table1_postgres',
    postgres_conn_id='andrey_postgres_localhost',
    sql='''
        CREATE TABLE IF NOT EXISTS raw_data_postgresoperator(
            id SERIAL PRIMARY KEY,
            year_month DATE NOT NULL,
            uf VARCHAR(20) NOT NULL,
            product VARCHAR(40) NOT NULL,
            unit CHAR(2) NOT NULL,
            volume DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP NOT NULL);
        ''',
    dag=dag)
# Transfere dados para Tabela raw_data_postgresoperator via PythonOperator
transfer_postgres = PostgresOperator(
    task_id='load_postgres_postgresoperator',
    postgres_conn_id='andrey_postgres_localhost',
    sql='''
        COPY raw_data_postgresoperator (id, year_month, uf, product, unit, volume, created_at) 
        FROM '/home/andreolv/airflow/dags/raw_data/raw_data.xlsx'
        DELIMITER ',' 
        CSV HEADER;;
        ''',
    dag=dag)
# --------------------------------------------
# Tarefa para transferrir dados para Postgres via PythonOperator
# Cria a Tabela raw_data_sqlalchemy
table2_postgres = PostgresOperator(
    task_id='create_table2_postgres',
    postgres_conn_id='andrey_postgres_localhost',
    sql='''
        CREATE TABLE IF NOT EXISTS raw_data_sqlalchemy(
            id SERIAL PRIMARY KEY,
            year_month DATE NOT NULL,
            uf VARCHAR(20) NOT NULL,
            product VARCHAR(40) NOT NULL,
            unit CHAR(2) NOT NULL,
            volume DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP NOT NULL);
        ''',
    dag=dag)    
# Transfere dados para Tabela raw_data_sqlalchemy via PythonOperator
python_postres = PythonOperator(
    task_id = 'load_postgres_pythonoperator',
    python_callable=load_postgres_python,
    dag=dag)

send_message_email = EmailOperator(
    task_id='send_email',
    to="andreyyolv@gmail.com",
    subject="[AIRFLOW] Pipeline Raizen Completed",
    html_content="<h3>Congratulations Andrey! Your pipeline was successful completed!</h3>",
    trigger_rule="one_success",
    dag=dag)

send_message_telegram = TelegramOperator(
    task_id='send_telegram',
    telegram_conn_id='telegram',
    chat_id='1675567088',               #your telegram chat_id 
    text='Your pipeline was successful completed!',
    trigger_rule="one_success",
    dag=dag)

# [START task_sequence]
# Tarefa que se divide em Y
is_excel_file_available >> [e1, e10]

# Tarefas lineares
e1 >> t1 >> t2 >> t3 >> t4 >> t5

e10 >> t10 >> t20 >> t30 >> t40 >> t50

# Tarefas que se unem em Y
[t5, t50] >> conc >> verifyload >> [deletefiles, table1_postgres, table2_postgres]

table1_postgres >> transfer_postgres

table2_postgres >> python_postres

[python_postres, transfer_postgres] >> send_message_email

[python_postres, transfer_postgres] >> send_message_telegram
# [END task_sequence]