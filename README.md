# fastapi_template
A FastAPI project template with user support

Built with Python, FastAPI, Ariadne, Postgres, [Docker](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker)


## Dev Requirements:
- Docker
- Docker Compose
- [Optional] Visual Studio Code w/ Remote Containers extension
- [Optional] Add to local hosts 127.0.0.1 yourdomain for testing social login


## Run:
Run with docker-compose up specifying the dev compose file (or use convenience scripts) and open shell to container as needed.
Source folder is mounted and server auto-reloads on change.

Alternatively, in VS Code -> View -> Command Palette... -> Remote-Containers: Open Folder in Container...

Access relevant dev links [http://localhost](http://localhost)

Access OpenAPI docs [http://localhost/docs](http://localhost/docs)

Access PG Admin [http://localhost:5052](http://localhost:5052)

### Commands:
- $ docker-compose -p fastapi_template -f docker-compose.dev.yml build
- $ docker-compose -p fastapi_template -f docker-compose.dev.yml up
- $ docker-compose -p fastapi_template -f docker-compose.dev.yml down
- $ docker exec -it fastapi_template_app_1 bash

### Convenience Scripts:
- $ sh build.sh
- $ sh run.sh
- $ sh stop.sh
- $ sh connect.sh

### Database:
Created at container start up (prestart.sh). Trash _tmp/db to clear data.

### Lint:
- $ sh lint.sh

### Tests:
- $ pytest