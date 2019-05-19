FROM python:3.7
LABEL maintainer="mookrs"

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /fanbot

ENTRYPOINT ["python", "manage.py"]
