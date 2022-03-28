# https://airflow.apache.org/docs/apache-airflow/stable/start/local.html
# [START import_module]
from re import L
from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
import time
import pandas as pd
# [END import_module]
# --------------------------------------------------------------------------------------------------------
# [START defining variables]
month_map = {'Jan':'01', 'Fev':'02', 'Mar':'03', 'Abr': '04', 'Mai':'05', 'Jun':'06',
            'Jul':'07', 'Ago':'08', 'Set':'09', 'Out':'10', 'Nov':'11', 'Dez':'12',
            'COMBUSTÍVEL':'product', 'ESTADO': 'uf'}

column_names_ordered = ["year_month", "uf", "product", "unit", "volume", "created_at"]
# [END defining variables]
# --------------------------------------------------------------------------------------------------------
# [START python functions]
# Funções para as DAGs da Tabela 2
def extract_table_1():
    df1 = pd.read_excel("vendas-combustiveis-m3.xlsx", sheet_name='DPCache_m3')

def transform_table_1():
    # Converte o nome das colunas do dataframe
    df1.rename(columns = month_map, inplace = True)
    # Remove as colunas que não são necessárias
    df1 = df1.drop(['REGIÃO', 'TOTAL'], axis=1)
    # Pivoteia as colunas dos meses para linhas
    df3 = pd.melt(df1, id_vars=["product", "ANO", "uf"], var_name="MES", value_name='volume')
    # Força o tipo da coluna ano para string para facilitar concatenação posterior
    df3 = df3.astype({"ANO":str})
    # Concatena o ano com o mes para formar a coluna year_month
    df3['year_month'] = df3.ANO.str.cat(df3.MES,sep="-")
    # Remove as colunas ano e mes, agora não mais necessárias
    df3 = df3.drop(['ANO', 'MES'], axis=1)
    # Cria a coluna unit que é sempre igual a 'm3'
    df3['unit'] = "m3"
    # Cria a coluna created_at que é sempre igual ao timestamp atual
    df3['created_at'] = pd.Timestamp.now()
    # Remove a unidade de medida 'm3' do final de cada linha da coluna product
    df3['product'] = df3['product'].str[0:-5]
    # Ordena as colunas do dataframe pela ordem indicada no github do teste
    df3 = df3[column_names_ordered]
    # Remove linhas em que o volume é NaN/vazio pra facilitar a inserção no banco de dados
    df3 = df3.dropna(subset = ['volume'])
    
def verify_table_1():
    time.sleep(10)


# --------------------------------------------------
# Funções para as DAGs da Tabela 2
def extract_table_2():
    df2 = pd.read_excel("vendas-combustiveis-m3.xlsx", sheet_name='DPCache_m3_2')

def transform_table_2():
    # Converte o nome das colunas do dataframe
    df2.rename(columns = month_map, inplace = True)
    # Remove as colunas que não são necessárias
    df2 = df2.drop(['REGIÃO', 'TOTAL'], axis=1)
    # Pivoteia as colunas dos meses para linhas
    df4 = pd.melt(df2, id_vars=["product", "ANO", "uf"], var_name="MES", value_name='volume')
    # Força o tipo da coluna ano para string para facilitar concatenação posterior
    df4 = df4.astype({"ANO":str})
    # Concatena o ano com o mes para formar a coluna year_month
    df4['year_month'] = df4.ANO.str.cat(df4.MES,sep="-")
    # Remove as colunas ano e mes, agora não mais necessárias
    df4 = df4.drop(['ANO', 'MES'], axis=1)
    # Cria a coluna unit que é sempre igual a 'm3'
    df4['unit'] = "m3"
    # Cria a coluna created_at que é sempre igual ao timestamp atual
    df4['created_at'] = pd.Timestamp.now()
    # Remove a unidade de medida 'm3' do final de cada linha da coluna product
    df4['product'] = df4['product'].str[0:-5]
    # Ordena as colunas do dataframe pela ordem indicada no github do teste
    df4 = df4[column_names_ordered]
    # Remove linhas em que o volume é NaN/vazio pra facilitar a inserção no banco de dados
    df4 = df4.dropna(subset = ['volume'])

def verify_table_2():
    time.sleep(10)

# --------------------------------------------------------------------------------------------------------
# Funções para as DAGs da junção e carregamento das tabelas
def load_tables():
    # Concatena os dataframes df3 e df4
    raw_data = pd.concat([df3, df4], ignore_index=True)
    # Exporta o dataframe concatenado raw para um arquivo de formato 'xlsx'
    raw_data.to_excel('raw_data.xlsx')

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
    'retry_delay': timedelta(minutes=2)}
# [END default_args]
# --------------------------------------------------------------------------------------------------------
# [START instantiate_dag]
dag = DAG(
    'andrey_pipeline',
    default_args=default_args,
    start_date=datetime(2022, 3, 26),
    schedule_interval=timedelta(minutes=60),
    tags=['raizen', 'oportunidade', 'uhull'])
# [END instantiate_dag]
# --------------------------------------------------------------------------------------------------------
# [START basic_task]
# Tarefas para a tabela 1
e1 = PythonOperator(
     task_id = 'extract1',
     python_callable=extract_table_1,
     dag=dag)

t1 = PythonOperator(
     task_id = 'transform1',
     python_callable=transform_table_1,
     dag=dag)

v1 = PythonOperator(
     task_id = 'verify1',
     python_callable=verify_table_1,
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

v2 = PythonOperator(
     task_id = 'verify2',
     python_callable=verify_table_2,
     dag=dag)
# --------------------------------------------
# Tarefa para a junção das tabelas e carregamento   
l = PythonOperator(
     task_id = 'load',
     python_callable=load_tables,
     dag=dag)
# [END basic_task]
# --------------------------------------------------------------------------------------------------------
# [START task_sequence]
e1 >> t1 >> v1 >> l

e2 >> t2 >> v2 >> l
# [END task_sequence]
