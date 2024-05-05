from datetime import datetime
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
from airflow.hooks.base import BaseHook
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')

# Function to read and clean CSV file
def read_and_clean_csv():
    # Read raw_weather_NPM.csv file       
    weather_df = pd.read_csv(AIRFLOW_HOME + '/dags/data/raw_weather_NPM.csv')
    weather_df.drop(columns=['Unnamed: 0', 'tsun', 'wpgt', 'snow'], inplace=True)
    weather_df['pres'].fillna(round(weather_df['pres'].mean(),2), inplace=True)
    weather_df['wspd'].fillna(round(weather_df['wspd'].mean(),2), inplace=True)
    weather_df['wdir'].fillna(round(weather_df['wdir'].mean(),2), inplace=True)
    weather_df['tmax'].fillna(round(weather_df['tmax'].mean(),2), inplace=True)
    weather_df['prcp'].fillna(round(weather_df['prcp'].mean(),2), inplace=True)
    weather_df['tmin'].fillna(round(weather_df['tmin'].mean(),2), inplace=True)
    weather_df['tavg'].fillna(round(weather_df['tavg'].mean(),2), inplace=True)

    # Connect to PostgreSQL and insert data into Weather table
    #engine = create_engine('postgresql://airflow:airflow@host.docker.internal:5432/weather')
    conn = BaseHook.get_connection('postgres_default')
    engine = create_engine(f'postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}')
    weather_df.to_sql('Weather', engine, if_exists='replace', index=False)

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retry_delay': timedelta(minutes=5),
    'retries': 5,
}

# Define the DAG
dag = DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='A DAG to read, clean, and insert weather data into PostgreSQL',
    schedule_interval=None,
)

# Task 1: Read and clean CSV file
task_read_clean_csv = PythonOperator(
    task_id='read_and_clean_csv',
    python_callable=read_and_clean_csv,
    dag=dag,
)

# Task 2: Fetch data from PostgreSQL and display
def fetch_and_display_data():
    # เชื่อมต่อกับ PostgreSQL
    conn = BaseHook.get_connection('postgres_default')
    engine = create_engine(f'postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}')

    # ดึงข้อมูลจาก Table Weather
    weather_df = pd.read_sql_table('Weather', engine)

    # แสดงผลข้อมูล
    print(weather_df.to_string())

task_fetch_display_data = PythonOperator(
    task_id='fetch_and_display_data',
    python_callable=fetch_and_display_data,
    dag=dag,
)

# Set task dependencies
task_read_clean_csv >> task_fetch_display_data
