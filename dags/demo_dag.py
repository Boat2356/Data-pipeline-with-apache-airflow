from datetime import datetime
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
from airflow.hooks.base import BaseHook
from pathlib import Path
import requests
import numpy as np
from airflow.models import Variable


AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
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

# Function to extract data from API
def extract_data_from_API():
  url = "https://meteostat.p.rapidapi.com/stations/daily"
  querystring = {"station":"48357","start":"2018-01-01","end":"2023-01-31"} #48357 : Air monitoring station in Nakhon Phanom Province
  rapidapi_key = Variable.get("meteostat_weather_API_KEY")
  headers = {
	"X-RapidAPI-Key": rapidapi_key,
	"X-RapidAPI-Host": "meteostat.p.rapidapi.com"
  }
  response = requests.get(url, headers=headers, params=querystring)  
  weather = response.json()['data']
  weather_df = pd.DataFrame()
  for i in weather:
    df = pd.DataFrame.from_dict([i])
    weather_df = pd.concat([weather_df,df],ignore_index=True)
  filepath = Path('dags/data/weather_NPM_station.csv')  
  filepath.parent.mkdir(parents=True, exist_ok=True)  
  weather_df.to_csv(filepath)  

# Task 1: Extract data from API
task_extract_data_from_API = PythonOperator(
    task_id='extract_data_from_API',
    python_callable=extract_data_from_API,
    dag=dag,
)

# Function to read and clean CSV file
def read_and_clean_csv():
    # Read raw_weather_NPM.csv file       
    weather_df = pd.read_csv(AIRFLOW_HOME + '/dags/data/weather_NPM_station.csv')
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


# Task 2: Read and clean CSV file
task_read_clean_csv = PythonOperator(
    task_id='read_and_clean_csv',
    python_callable=read_and_clean_csv,
    dag=dag,
)

# Task 3: Fetch data from PostgreSQL and display
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
task_extract_data_from_API >> task_read_clean_csv >> task_fetch_display_data
