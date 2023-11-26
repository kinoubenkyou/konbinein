FROM python:3.11.1
RUN pip install poetry==1.7.1
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry install
