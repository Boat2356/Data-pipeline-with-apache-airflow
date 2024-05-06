# Weather Data Pipeline with Apache Airflow
## The tools used in this project.
- Apache airflow
- Docker
- Visual studio code
- DBeaver

## Project Flow Diagram

<p align="center">
  <img width="543" height="226" src="https://github.com/Boat2356/Data-pipeline-with-apache-airflow/assets/140761543/52d2f5ea-47ee-4099-b988-e8d9bfb15123">
</p>

## About Meteostat API
The Meteostat JSON API offers easy access to historical weather and climate data, filtered by weather station or location, and optional parameters.
- You can visit this API endpoint here: [Meteostat Developers](https://dev.meteostat.net/api/stations/daily.html)

## Process Explanation
### Process Overview
- The DAG is designed to fetch weather data from an API, clean it, and store it in a PostgreSQL database.
- It consists of three tasks: extract_data_from_API, read_and_clean_csv, and fetch_and_display_data.
- The tasks are executed in the following order: extract_data_from_API -> read_and_clean_csv -> fetch_and_display_data.

### Airflow
- Airflow is an open-source platform for programmatically authoring, scheduling, and monitoring workflows.
- In this case, Airflow is used to orchestrate the weather data pipeline.
- The DAG (weather_data_pipeline) is defined in a Python file (demo_dag.py) placed in the dags directory.

### Installing Docker
- Docker is a platform for building, deploying, and running applications using containers.
- To install Docker on Ubuntu, run the following bash commands:
```
sudo apt-get update
sudo apt-get install docker.io
```
- For other operating systems, follow the official Docker installation guide: https://docs.docker.com/get-docker/

### Docker Environment Variables (.env)
- Create a .env file in the project root directory to store environment variables.
- This file should contain variables like the PostgreSQL database credentials, Airflow credentials, and any other sensitive information.
- Example contents of .env:
```
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

### Docker Compose (docker-compose.yml)
- Docker Compose is a tool for defining and running multi-container Docker applications.
- Create a docker-compose.yml file in the project root directory to define the services (containers) required for the application.
- This file typically includes services for Airflow (WebServer, Scheduler, and Workers), PostgreSQL database, and any other required services.
- Example docker-compose.yml file:
```
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
  webserver:
    build: .
    env_file:
      - .env
    depends_on:
      - postgres
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
volumes:
  postgres-db-volume:
```

### Dockerfile
- The Dockerfile is a text document that contains instructions for building a Docker image.
- It specifies the base image, installs required packages, copies the application code, and sets the entry point for the container.
- Example Dockerfile:
```
FROM apache/airflow:2.2.3
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pandas \
    python3-requests \
    && rm -rf /var/lib/apt/lists/*
USER airflow
COPY requirements.txt .
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" -r requirements.txt
```

### Requirements.txt:
- This file lists the Python packages required by the application.
- Airflow and its dependencies are typically installed from the constraints file specified in the Dockerfile.
- Additional packages like pandas and requests should be listed in the requirements.txt file.

### Database
- PostgreSQL is used as the database to store the weather data.
- The database connection details (host, port, user, password, and schema) are retrieved from the Airflow connections (specified in the BaseHook.get_connection method).

### Running the Application
- Navigate to the project root directory in your terminal.
- Build and start the Docker containers using Docker Compose:
```
docker-compose up --build
```
- Access the Airflow WebUI at http://localhost:8080 (default credentials: airflow/airflow).

### DBeaver
#### Installing DBeaver:
DBeaver is a free and open-source universal database tool that supports various database management systems, including PostgreSQL. To install DBeaver, follow these steps:
1. Visit the official DBeaver website: https://dbeaver.io/download/
2. Download the appropriate version for your operating system (Windows, macOS, or Linux).
3. Extract the downloaded archive file.
4. Run the DBeaver executable file to launch the application.

#### Connecting to the Database:
Once DBeaver is installed, you can connect to your PostgreSQL database by following these steps:
1. Open DBeaver.
2. In the Database Navigator panel, right-click and select "New Connection".
3. In the "Create new connection" window, select "PostgreSQL" from the list of available database drivers.
4. Configure the connection details:
- Host: Enter the hostname or IP address of your PostgreSQL server (e.g., localhost or host.docker.internal).
- Port: Enter the port number on which your PostgreSQL server is running (e.g., 5432).
- Database: Enter the name of the database (e.g., airflow).
- User: Enter the username for the database (e.g., airflow).
- Password: Enter the password for the database user.
5. Click "Test Connection" to verify the connection details. If the connection is successful, click "Finish" to create the connection.
  
#### Querying Data:
After establishing the connection, you can query data from the "Weather" table using SQL queries. Here's an example:
1. In the Database Navigator panel, expand the connection node and navigate to the "Weather" table.
2. Right-click on the "Weather" table and select "View Data".
3. This will open the Data Editor window, where you can see the data in the table.
4. To run a SQL query, click the SQL Editor icon (or press F8) to open the SQL Editor window.
5. Enter the following SQL query to fetch all records from the "Weather" table:
```
SELECT * FROM "Weather";
```
6. Click the "Execute SQL Statement" button (or press F9) to execute the query. The query result will be displayed in the SQL Editor window.
