# Netflix_DataEngineering_Project

## What is this project?

This is an end-to-end data engineering project I built on **Microsoft Azure**. The idea was to simulate a real-world data pipeline — taking raw Netflix data from GitHub, processing it through multiple layers, and making it available for analytics.

I used **Azure Data Factory, ADLS Gen2, Azure Databricks, Delta Live Tables, and Azure Synapse Analytics** to build this.

---

## Architecture

![Architecture](https://github.com/PusaAkshay/Netflix_DataEngineering_Project/blob/da16a6142d1ec59ade92cc10c13e45d6e0e862e5/Architecture.png)

```
GitHub (Source)
      ↓
Azure Data Factory
(Web Activity → Set Variable → ForEach → Copy Activity)
      ↓
ADLS Gen2
  ├── Raw Layer      ← netflix_titles lands here
  ├── Bronze Layer   ← ADF + Autoloader writes here
  ├── Silver Layer   ← PySpark transformations
  ├── Gold Layer     ← DLT (Unity Catalog) + Synapse CETAS
  └── Metastore      ← Unity Catalog metadata
      ↓
Azure Databricks
  ├── Autoloader (Spark Streaming) → Bronze
  ├── Silver Transformations       → Silver
  └── DLT Pipeline                 → Gold (Unity Catalog)
      ↓
Azure Synapse Analytics (Serverless SQL Pool)
  ├── Reads Silver Delta via OPENROWSET
  ├── Writes Parquet to Gold container via CETAS
  └── External Tables + View for analytics
```

---

## Tech Stack

| Technology | How I used it |
|------------|---------------|
| Azure Data Factory | Ingested data from GitHub using Web Activity + ForEach + Copy Activity |
| Azure Data Lake Storage Gen2 | Storage for all layers — Raw, Bronze, Silver, Gold, Metastore |
| Azure Databricks | All processing — Autoloader, transformations, DLT pipeline |
| PySpark | Data cleaning and transformation in Silver layer |
| Spark Structured Streaming | Autoloader for incremental loading of netflix_titles |
| Spark Declarative Pipelines (DLT) | Built Gold layer with automated data quality checks |
| Delta Lake | Storage format used across Bronze, Silver, Gold |
| Unity Catalog | Governance — all DLT tables registered here |
| Azure Synapse Analytics | Serverless SQL Pool — read Silver, write Gold as Parquet |
| GitHub | Source data + version control |

---

## Data Layers — Medallion Architecture

| Container | What's in it | Format | How it gets there |
|-----------|-------------|--------|-------------------|
| raw | netflix_titles.csv | CSV | Placed manually from GitHub |
| bronze | All 5 Netflix files | Delta | ADF pipeline + Autoloader |
| silver | Cleaned 5 datasets | Delta | PySpark transformation notebooks |
| gold | 5 tables as Parquet | Parquet | Synapse CETAS from Silver |
| metastore | DLT Gold tables | Delta | DLT pipeline via Unity Catalog |

**One thing worth noting** — because Unity Catalog was enabled, I couldn't set an explicit `path=` in the DLT decorators. So DLT tables landed in the metastore container instead of the gold container. To still populate the gold container, I used Synapse Serverless SQL to read from Silver and write Parquet to Gold via CETAS.

---

## How the pipeline works

### Step 1 — ADF gets data from GitHub
I built an ADF pipeline that calls the GitHub API using a Web Activity, stores the file list in a variable, loops through each file with ForEach, and copies them into the Bronze container using Copy Activity.

Files loaded this way: `netflix_cast`, `netflix_directors`, `netflix_countries`, `netflix_category`

### Step 2 — Autoloader loads netflix_titles
`netflix_titles` was placed in the Raw container. Autoloader picks it up using Spark Structured Streaming and loads it incrementally into Bronze. This handles schema inference automatically.

### Step 3 — Silver transformations
PySpark notebooks clean and transform all 5 Bronze datasets — handle nulls, fix data types, rename columns — and write them as Delta tables to the Silver container.

### Step 4 — DLT Pipeline builds Gold
I used Spark Declarative Pipelines (DLT) to read from Silver and create Gold tables. Each table has a data quality rule using `expect_all_or_drop`. The pipeline creates 7 tables including a staging table, a transformation view, and the final gold table.

### Step 5 — Synapse loads Gold container
Synapse Serverless SQL reads Silver Delta files using OPENROWSET and writes them as Parquet to the Gold container using CETAS. External tables and a joined view are created on top.

### Step 6 — Databricks Jobs ties everything together
Everything runs as a single Databricks Job:

```
Autoloader (5m 41s) → lookuppath (5m 10s) → foreach_iteration (1m 6s)
      → silverTransformation (13s) → Gold_layer_DLT (1m 11s)
```




## Project Structure

```
Netflix_DataEngineering_Project/
│
├── adf/
│   ├── datasets/
│   ├── factories/
│   ├── linked_services/
│   └── pipelines/
│
├── databricks/
│   ├── auto_loader.py
│   ├── silver_lookup.py
│   ├── silver_load_layer.py
│   ├── silver_transformation.py
│   └── DLT_Gold_Layer01.py
│
├── synapse/
│   └── external_tables.sql
│
└── README.md
```

---

## Screenshots

### ADF Pipeline
![ADF](https://github.com/PusaAkshay/Netflix_DataEngineering_Project/blob/7cb31573d57556ff5d1a5c3a26738ede637e3095/ADF.png)

### Databricks Jobs Run ✅
![jobs](https://github.com/PusaAkshay/Netflix_DataEngineering_Project/blob/7cb31573d57556ff5d1a5c3a26738ede637e3095/JOBS.png)

### DLT Pipeline — 7 Tables ✅
![DLT](https://github.com/PusaAkshay/Netflix_DataEngineering_Project/blob/7cb31573d57556ff5d1a5c3a26738ede637e3095/DLT_PIPELINE.png)

---

## What I'd add next

- Connect Power BI for dashboards
- Set up CI/CD with Azure DevOps
- Add more specific data quality rules per table
- Look into SCD Type 2 for slowly changing data
- Add pipeline monitoring with Azure Monitor

---

