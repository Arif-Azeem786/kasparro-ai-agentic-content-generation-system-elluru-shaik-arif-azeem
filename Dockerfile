# Dockerfile - simple image to run pipeline
FROM python:3.10-slim

# create app dir
WORKDIR /app

# copy requirements first to leverage cache
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# copy project
COPY . /app

# set env defaults
ENV PYTHONUNBUFFERED=1
ENV ENABLE_RETRIEVAL=0
ENV OPENAI_API_KEY=""

# default command: run pipeline
CMD ["python", "-m", "src.main"]
