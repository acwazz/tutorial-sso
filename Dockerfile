FROM --platform=linux/amd64 python:3.9
RUN apt-get update
RUN apt-get clean && rm -fr /var/lib/apt/lists/* && rm -fr /tmp/*
RUN pip install --upgrade pip
WORKDIR /backend
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
CMD  ["hypercorn", "--config", "file:./hypercorn_config.py", "sso_service.main:app"]