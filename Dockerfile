FROM python:3.7
LABEL maintainer="mookrs"

RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /fanbot

ENTRYPOINT ["python", "manage.py"]
