FROM python:3.12.3
WORKDIR /app
COPY requirements.txt reqs
RUN pip install -r reqs
COPY api.py api.py
COPY chromadb_populate.py chromadb_populate.py
CMD uvicorn api:app --host 0.0.0.0 --port 8000