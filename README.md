# Evaluation of Scalability and Distributed Performance

This repository contains necessary coponets to investigate how different architectures in MongoDB perform, on standalone deployment and sharded deployment.

---

## Quick Start

### Clone the repository

```bash
git clone https://github.com/jiangfz1997/Blog_MongoDB.git
```

### Switch branch

```bash
git checkout allen-scaling-and-replication
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
Start all services in standalone mode:

```bash
docker compose --env-file .env.standalone --profile standalone up -d 
```

or if you wish to run the sharded cluster

```bash
docker compose --env-file .env.sharded --profile sharded up -d 
```

To stop all services:

```bash
docker compose down
```

If you want to clean up unused containers:

```bash
docker compose down --remove-orphans
```

**You MUST stop previewly run containers before switching to a differnt architecture**
### FastAPI Development Server

Run the backend manually:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

This backend connects to the same MongoDB instance (default URI `mongodb://localhost:27017`).

Swagger UI is available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Load test
Locust is used for load testing the FastAPI backend. To run locust, refer to the README.MD under `load_test` folder. 

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

* If using Linux or MACOS, cadvisor can be used instead of Node Exporter for container metrics.
* You can modify `prometheus.yml` to add more targets or scrape intervals.
* Grafana dashboards can be customized by exporting new JSONs from the UI.
---
