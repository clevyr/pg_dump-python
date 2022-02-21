FROM postgres:11-alpine as postgres
FROM python:3.11.0a5-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY --from=postgres /usr/local/bin/pg_dump /usr/local/bin/pg_dump
COPY --from=postgres /usr/local/lib/libpq.so.5.11 /usr/local/lib/libpq.so.5

COPY . .

CMD [ "python", "-u", "/app/main.py" ]
