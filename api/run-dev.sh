set -x
uvicorn --reload --reload-dir ./app app.main:app --host 0.0.0.0 --port 8000
