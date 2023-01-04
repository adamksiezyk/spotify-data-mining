# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

RUN pip install pipenv

ENV PROJECT_DIR=/usr/local/src/webapp
ENV FLASK_APP=service/app.py
ENV LOG_CONF=${PROJECT_DIR}/logging.conf

WORKDIR ${PROJECT_DIR}

COPY Pipfile Pipfile.lock ${PROJECT_DIR}/

COPY . ${PROJECT_DIR}/

RUN pipenv install --system --deploy

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
