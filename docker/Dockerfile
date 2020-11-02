FROM python:3.9.0-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry==1.1.3

WORKDIR /code

COPY poetry.lock /code
COPY pyproject.toml /code
COPY ./src /code/src/

RUN poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT python3 /code/src/app.py
