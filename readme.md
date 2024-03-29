# FastAPI-Template

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

* jenkins
* psycopg/jsonb, sqlmodel, sqlalchemy, alembic

### FastAPI-Template

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
docker compose -p fastapi-template -f docker/compose.yml build
docker compose -p fastapi-template -f docker/compose.yml up

docker exec -it fastapi-template-api-1 bash

docker compose -p fastapi-template -f docker/compose.yml down
```

### Work with API container directly

```
docker build . -t fastapi-template/api -f docker/Dockerfile.api
docker run --env-file docker/env/api.env --env-file docker/env/db.env -p 8000:8000 fastapi-template/api
```

## Run

### Run locally

* Need to setup env variables and have db and cache services running on host

```
uvicorn --reload --reload-dir ./app app.main:app --host 0.0.0.0 --port 8000
```

### Start the containers

```
docker compose -p fastapi-template -f docker/compose.yml up
```

### With app running

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

pytest --cov-config=pyproject.toml --cov --cov-report html
pytest --cov-config=pyproject.toml --cov --cov-report xml

docker compose -p fastapi-template -f docker/compose.yml --profile sonar up
docker compose -p fastapi-template -f docker/compose.yml --profile sonar-scanner up

mutmut run
mutmut html
```

## Lint

### Lint the code

```
<from api dir>
flake8 app
flake8 tests

pylint app --rcfile pyproject.toml
pylint tests --rcfile pyproject.toml --disable=redefined-outer-name

pyreverse -o png -p Pyreverse app
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
