# Blog Monitoring Stack (FastAPI + MongoDB + Prometheus + Grafana)

This repository contains a **containerized monitoring and database stack** used for analyzing and visualizing the performance of a MongoDB-based FastAPI blog system.
It includes MongoDB, Prometheus, Grafana, and Node/MongoDB exporters — all orchestrated via **Docker Compose**.

---

## Quick Start

### Clone the repository

```bash
git clone https://github.com/jiangfz1997/Blog_MongoDB.git
cd Blog_MongoDB
```

### Set up Python environment

For FastAPI backend or script usage:

```bash
# python version 3.11+
pip install -r requirements.txt
```
---

### Run the full system with Docker Compose
Note: Backend FastAPI server is not included in the Docker Compose setup for development purposes.
It needs to be run separately (see below).
Start all services in detached mode:

```bash
docker compose up -d
```

To stop all services:

```bash
docker compose down
```

If you want to clean up unused containers:

```bash
docker compose down --remove-orphans
```
### FastAPI Development Server

Run the backend manually:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

This backend connects to the same MongoDB instance (default URI `mongodb://localhost:27017`).

Swagger UI is available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Load test
Locust is used for load testing the FastAPI backend. To run locust:

```bash
locust -f locust_test.py --host http://localhost:8000
```

Then open [http://localhost:8089](http://localhost:8089) in your browser to access the Locust web interface.

Log tracking still under development.

---

## Services Overview

| Service            | Description                                                 | Port    |
| ------------------ | ----------------------------------------------------------- | ------- |
| **MongoDB**        | Primary database storing blog posts, user data, etc.        | `27017` |
| **Mongo Exporter** | Exposes MongoDB internal metrics to Prometheus.             | `9216`  |
| **Node Exporter**  | Exposes host & container-level metrics (CPU, memory, disk). | `9100`  |
| **Prometheus**     | Scrapes metrics from exporters, stores time-series data.    | `9090`  |
| **Grafana**        | Visualization layer for metrics dashboards.                 | `3000`  |

---

## Grafana Dashboards

Once the containers are up:

* Visit **Grafana UI** → [http://localhost:3000](http://localhost:3000)
* Default credentials:
  **user:** `admin`
  **password:** `admin`
* Add the **Prometheus data source** (URL: `http://prometheus:9090`)
* Import dashboards from the `dashboards/` folder:

  * `MongoDB_Instances_Overview.json` – MongoDB operations and latency visualization
  * Other panels include CPU, memory, and request throughput

---

## Cleanup and Maintenance

To remove all containers and volumes:

```bash
docker compose down -v
```

To view logs for debugging:

```bash
docker compose logs -f mongo
docker compose logs -f prometheus
docker compose logs -f grafana
```


## Notes

* The Node Exporter installation script automatically runs inside the MongoDB container (see `node-exporter-install.sh`).
* If using Linux or MACOS, cadvisor can be used instead of Node Exporter for container metrics.
* You can modify `prometheus.yml` to add more targets or scrape intervals.
* Grafana dashboards can be customized by exporting new JSONs from the UI.
---
