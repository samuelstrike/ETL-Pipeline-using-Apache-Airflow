# 🌍 NASA EONET ETL Pipeline

This repository contains a complete ETL pipeline that fetches natural event data from the [NASA EONET API](https://eonet.gsfc.nasa.gov/api/v3/events) and loads it into a PostgreSQL database using **Apache Airflow** and **PostgresHook**.

## 📌 Project Overview

This ETL pipeline demonstrates:

- Extracting data from a public API (NASA EONET)
- Transforming and inserting event data into a PostgreSQL table
- Automating and orchestrating the pipeline with Apache Airflow
- Avoiding temporary JSON storage and directly using SQL operators and hooks

> 🔁 The EONET API is dynamic and continuously updated, so this pipeline is designed to ingest all available events each run and gracefully upsert data into the database.

---

## 🛠️ Tools & Technologies

- **Apache Airflow** – Orchestration tool
- **PostgreSQL** – Destination data warehouse
- **Python** – Core language used for data transformation
- **PostgresHook & SQLExecuteQueryOperator** – Airflow providers for database access
- **Docker** – For local environment setup

---

## 📐 Architecture

![Architecture Diagram](images/elt_architecture.png

---

## 🧱 Database Schema

```sql
CREATE TABLE IF NOT EXISTS nasa_events (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    category TEXT,
    source TEXT,
    geometry_type TEXT,
    coordinates TEXT,
    date TIMESTAMP
);

