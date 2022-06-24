# docker build . -t api-template/api -f docker/Dockerfile 
# docker run -d -p 8000:8000 api-template/api

FROM python:3.9-slim-bullseye

WORKDIR /app/api

COPY ./api/requirements/api_requirements.txt ./requirements/

RUN pip install -r requirements/api_requirements.txt

COPY ./api/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["sleep", "infinity"]