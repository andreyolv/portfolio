# https://airflow.apache.org/docs/apache-airflow/stable/start/local.html
# [START import_module]
from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
# from airflow.operators.postgres_operator import PostgresOperator
# from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email import EmailOperator   
# from airflow.providers.telegram.operators.telegram import TelegramOperator
from sqlalchemy import create_engine
import time
import pandas as pd
import numpy as np
# [END import_module]
# --------------------------------------------------------------------------------------------------------
# [START defining variables]
filepath = f'/home/andreolv/airflow/dags/files/vendas-combustiveis-m3.xlsx'

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
    df1 = pd.read_excel(filepath, sheet_name='DPCache_m3')
    return df1.to_json()

def transform_table_1():
    global df1
    df1 = pd.read_json(df1)
    # Converte o nome das colunas do dataframe
    df1.rename(columns = month_map, inplace = True)
    # Remove as colunas que não são necessárias
    df1 = df1.drop(['REGIÃO', 'TOTAL'], axis=1)
    # Pivoteia as colunas dos meses para linhas
    df1 = pd.melt(df1, id_vars=["product", "ANO", "uf"], var_name="MES", value_name='volume')
    # Força o tipo da coluna ano para string para facilitar concatenação posterior
    df1 = df1.astype({"ANO":str})
    # Concatena o ano com o mes para formar a coluna year_month
    df1['year_month'] = df1.ANO.str.cat(df1.MES,sep="-")
    # Remove as colunas ano e mes, agora não mais necessárias
    df1 = df1.drop(['ANO', 'MES'], axis=1)
    # Cria a coluna unit que é sempre igual a 'm3'
    df1['unit'] = "m3"
    # Cria a coluna created_at que é sempre igual ao timestamp atual
    df1['created_at'] = pd.Timestamp.now()
    # Remove a unidade de medida 'm3' do final de cada linha da coluna product
    df1['product'] = df1['product'].str[0:-5]
    # Ordena as colunas do dataframe pela ordem indicada no github do teste
    df1 = df1[column_names_ordered]
    # Remove linhas em que o volume é NaN/vazio pra facilitar a inserção no banco de dados
    df1 = df1.dropna(subset = ['volume'])
    return df1.to_json()
# --------------------------------------------------
# Funções para as DAGs da Tabela 2
def extract_table_2():
    df2 = pd.read_excel(filepath, sheet_name='DPCache_m3_2')
    return df2.to_json()

def transform_table_2():
    global df2
    df2 = pd.read_json(df2)
    # Converte o nome das colunas do dataframe
    df2.rename(columns = month_map, inplace = True)
    # Remove as colunas que não são necessárias
    df2 = df2.drop(['REGIÃO', 'TOTAL'], axis=1)
    # Pivoteia as colunas dos meses para linhas
    df2 = pd.melt(df2, id_vars=["product", "ANO", "uf"], var_name="MES", value_name='volume')
    # Força o tipo da coluna ano para string para facilitar concatenação posterior
    df2 = df2.astype({"ANO":str})
    # Concatena o ano com o mes para formar a coluna year_month
    df2['year_month'] = df2.ANO.str.cat(df2.MES,sep="-")
    # Remove as colunas ano e mes, agora não mais necessárias
    df2 = df2.drop(['ANO', 'MES'], axis=1)
    # Cria a coluna unit que é sempre igual a 'm3'
    df2['unit'] = "m3"
    # Cria a coluna created_at que é sempre igual ao timestamp atual
    df2['created_at'] = pd.Timestamp.now()
    # Remove a unidade de medida 'm3' do final de cada linha da coluna product
    df2['product'] = df2['product'].str[0:-5]
    # Ordena as colunas do dataframe pela ordem indicada no github do teste
    df2 = df2[column_names_ordered]
    # Remove linhas em que o volume é NaN/vazio pra facilitar a inserção no banco de dados
    df2 = df2.dropna(subset = ['volume'])
    return df2.to_json()
# --------------------------------------------------------------------------------------------------------
# Funções para as DAGs da junção e carregamento das tabelas
def concat_tables():
    global df1, df2
    df1 = pd.read_json(df1)
    df2 = pd.read_json(df2)
    # Concatena os dataframes df1 e df2
    raw_data = pd.concat([df1, df2], ignore_index=True)
    return raw_data.to_json()

def verify_tables():
    global raw_data
    raw_data = pd.read_json(raw_data)
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
    return raw_data.to_json()
    
def load_excel():
    global raw_data
    # Exporta o dataframe concatenado raw para um arquivo de formato 'xlsx'
    raw_data.to_excel('raw_data.xlsx')

def load_postgre():
    global raw_data
    # Cria a sessão entre 
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    # Carrega o dataframe concatenado raw no banco de dados PostgreSQL
    raw_data.to_sql('raw_data', con=engine, if_exists='append', index=False)

# [END python functions]
# --------------------------------------------------------------------------------------------------------
# [START default_args]
default_args = {
    'owner': 'Andrey Olv',
    'depends_on_past': False,
    'email': ['andreyyolv@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)}
# [END default_args]
# --------------------------------------------------------------------------------------------------------
# [START instantiate_dag]
dag = DAG(
    'andrey_pipeline',
    default_args=default_args,
    start_date=datetime(2022, 1, 1),
    schedule_interval="@monthly",   #@monthly = "0 0 1 * *"
    tags=['raizen', 'oportunidade', 'uhull']
)
# [END instantiate_dag]
# --------------------------------------------------------------------------------------------------------
# [START basic_task]
is_excel_file_available = FileSensor(
    task_id='is_excel_file_available',
    fs_conn_id="andrey_excel_path",
    filepath="vendas-combustiveis-m3.xlsx",
    poke_interval=60, # a cada quantos segundos ele vai tentar verificar se o arquivo existe
    timeout=60*10     # vai tentar ler 10 vezes
)
# --------------------------------------------
# Tarefas para a tabela 1
e1 = PythonOperator(
    task_id = 'extract1',
    python_callable=extract_table_1,
    dag=dag)

t1 = PythonOperator(
    task_id = 'transform1',
    python_callable=transform_table_1,
    dag=dag)
# --------------------------------------------
# Tarefas para a tabela 2
e2 = PythonOperator(
    task_id = 'extract2',
    python_callable=extract_table_2,
    dag=dag)

t2 = PythonOperator(
    task_id = 'transform2',
    python_callable=transform_table_2,
    dag=dag)
# --------------------------------------------
# Tarefa para a junção das tabelas e carregamento
conc = PythonOperator(
    task_id = 'concat',
    python_callable=concat_tables,
    trigger_rule="all_success",
    dag=dag)

verify = PythonOperator(
    task_id = 'verify',
    python_callable=verify_tables,
    dag=dag)

lo_ex = PythonOperator(
    task_id = 'load_excel',
    python_callable=load_excel,
    dag=dag)

lo_po = PythonOperator(
    task_id = 'load_postgres',
    python_callable=load_postgre,
    dag=dag)
    
"""
create_table = PostgresOperator(
    task_id='load_postgres',
    postgres_conn_id='postgres_default',
    sql='''
        CREATE TABLE IF NOT EXISTS raw_data (
        id SERIAL PRIMARY KEY,
        year_month DATA NOT NULL,
        uf CHAR(2) NOT NULL,
        product VARCHAR(40) NOT NULL,
        unit CHAR(2) NOT NULL,
        volume DOUBLE NOT NULL,
        created_at TIMESTAMP NOT NULL);
        ''',
    dag=dag)

send_message_telegram = TelegramOperator(
    task_id='send_message_telegram',
    telegram_conn_id='telegram_conn_id',
    chat_id='5151128933',
    text='Seu pipeline foi completado com sucesso!',
    dag=dag)
"""     
send_message_email = EmailOperator(
    task_id='send_message_email',
    to="andreyyolv@gmail.com",
    subject="Pipeline Raizen",
    html_content="<h3>raizen_pipeline_andrey</h3>",
    trigger_rule="all_success",
    dag=dag)
# [END basic_task]
# --------------------------------------------------------------------------------------------------------
# [START task_sequence]
is_excel_file_available >> [e1, e2]

e1 >> t1 >> conc

e2 >> t2 >> conc

conc >> verify >> [lo_ex, lo_po] >> send_message_email
# [END task_sequence]