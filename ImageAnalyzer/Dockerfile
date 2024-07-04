FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10


RUN apt-get update && \
    apt-get install -y docker.io

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install  --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
