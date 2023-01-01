# FastAPI-Beanie-POC

- [Overview](#overview)
- [Setup](#setup)
- [Run](#run)
- [Database](#database)
- [Cache](#cache)
- [Tests](#tests)
- [Lint](#lint)
- [Docs](#run)

## Overview

### Todo

* ui app
* perf tests
* pylint
* sonarqube
* jenkins
* psycopg/jsonb, sqlmodel, sqlalchemy, alembic

### POC exploring FastAPI with Beanie

* User auth support
* Todo app

### Tech stack

* Python
* MongoDB
* Redis
* JWT
* FastAPI
* Pydantic
* Beanie
* Pytest
* Factory Boy
* Locust

## Setup

### Requirements

* Docker
* Docker Compose
* Python 3.11 for local development

### Local setup

```
<from project root>
cp docker/env/api.env.example docker/env/api.env
cp docker/env/db.env.example docker/env/db.env

cd api

python3 -m venv venv

source venv/bin/activate

pip install -r requirements/requirements_api.txt
pip install -r requirements/requirements_dev.txt
pip install -r requirements/requirements_test.txt
```

### Docker setup

```
<from project root>
docker compose -p fastapi-beanie-poc -f docker/compose.yml build
docker compose -p fastapi-beanie-poc -f docker/compose.yml up

docker exec -it fastapi-beanie-poc-api-1 bash

pip install -r requirements/requirements_dev.txt
pip install -r requirements/requirements_test.txt

docker compose -p fastapi-beanie-poc -f docker/compose.yml down
```

### Work with API container directly

```
docker build . -t fastapi-beanie-poc/api -f docker/Dockerfile
docker run --env-file docker/env/api.env --env-file docker/env/db.env -p 8000:8000 fastapi-beanie-poc/api
```

## Run

### Run locally

* Need to setup env variables and have db and cache services running on host

```
uvicorn --reload --reload-dir ./app app.main:app --host 0.0.0.0 --port 8000
```

### Start the containers

```
docker compose -p fastapi-beanie-poc -f docker/compose.yml up
```

### With container running

* [http://localhost:8000](http://localhost:8000)
* [Health](http://localhost:8000/api/v1/health)
* [OpenAPI](http://localhost:8000/docs)

## Database

### With container running

* [DB admin](http://localhost:8001)

## Cache

### With container running

* [Cache admin](http://localhost:8002)

## Tests

### Run locally or from container

```
<from api dir>
pytest

pytest --cov=app tests --cov-branch --cov-report html:coverage

mutmut run
mutmut html
```

## Lint

### Lint the code

```
<from api dir>
flake8 app
flake8 tests
```

### Format the code

```
<from api dir>
sh lint.sh
```

## Docs

### Generate source code documentation

```
<from api dir>
pdoc --html --output-dir docs app
```
