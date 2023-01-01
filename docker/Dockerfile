# docker build . -t fastapi-beanie-poc/api -f docker/Dockerfile 
# docker run -d -p 8000:8000 fastapi-beanie-poc/api

FROM python:3.11-slim-bullseye

WORKDIR /app/api

COPY ./api/requirements/requirements_api.txt ./requirements/

RUN pip install -r requirements/requirements_api.txt

COPY ./api/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
