# dags/nasa_eonet_etl.py

import datetime
import pendulum
import requests
import json

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

API_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
POSTGRES_CONN_ID = "tutorial_pg_conn"  # Update this to match your Airflow connection ID

@dag(
    dag_id="nasa_eonet_etl",
    schedule="0 12 * * *",  # Runs daily at 12:00 UTC
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    tags=["nasa", "eonet", "etl"],
)
def nasa_eonet_etl():
    # Step 1: Create table for events
    create_events_table = SQLExecuteQueryOperator(
        task_id="create_events_table",
        conn_id=POSTGRES_CONN_ID,
        sql="""
            CREATE TABLE IF NOT EXISTS nasa_events (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                link TEXT,
                categories TEXT,
                sources TEXT,
                geometry JSONB,
                date_updated TIMESTAMP
            );
        """,
    )

    # Step 2: Fetch from API and insert to temp table

    @task
    def fetch_and_insert_events():
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        records = []
        for event in data.get("events", []):
            event_id = event.get("id")
            title = event.get("title")
            description = event.get("description", "")
            link = event.get("link")
            categories = ", ".join([c.get("title") for c in event.get("categories", [])])
            sources = ", ".join([s.get("id") for s in event.get("sources", [])])
            geometry = json.dumps(event.get("geometry", []))  # Convert dict/list to JSON string
            date_updated = event.get("geometry")[-1].get("date") if event.get("geometry") else None

            records.append((
                event_id,
                title,
                description,
                link,
                categories,
                sources,
                geometry,
                date_updated,
            ))

        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = postgres_hook.get_conn()
        cur = conn.cursor()

        insert_query = """
            INSERT INTO nasa_events (id, title, description, link, categories, sources, geometry, date_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                link = EXCLUDED.link,
                categories = EXCLUDED.categories,
                sources = EXCLUDED.sources,
                geometry = EXCLUDED.geometry,
                date_updated = EXCLUDED.date_updated;
        """

        cur.executemany(insert_query, records)
        conn.commit()

    create_events_table >> fetch_and_insert_events()

dag = nasa_eonet_etl()