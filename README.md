# fastapi_template
A FastAPI project template with user support

Built with Python, FastAPI, Ariadne, Couchbase, [Docker](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker)


## Dev Requirements:
- Docker
- Docker Compose
- [Optional] Visual Studio Code w/ Remote Containers extension
- [Optional] Add to local hosts 127.0.0.1 <yourdomain> for testing social login


## Run:
Run with docker-compose up specifying the dev compose file (or use convenience scripts) and open shell to container as needed.
Source folder is mounted and server auto-reloads on change.

Alternatively, in VS Code -> View -> Command Palette... -> Remote-Containers: Open Folder in Container...

Access relevant dev links [http://localhost](http://localhost)

Access OpenAPI docs [http://localhost/docs](http://localhost/docs)

Access Couchbase [http://localhost:8091/ui/index.html](http://localhost:8091/ui/index.html)

### Commands:
- $ docker-compose -f docker-compose.dev.yml build
- $ docker-compose -f docker-compose.dev.yml up
- $ docker-compose -f docker-compose.dev.yml down

### Convenience Scripts:
- $ sh dev_build.sh
- $ sh dev_start.sh
- $ sh dev_stop.sh

### Database:
Created at container start up (prestart.sh). Trash _tmp/db to clear data.

### Lint:
- $ sh lint.sh

### Tests:
- $ pytest