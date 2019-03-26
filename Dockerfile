FROM postgres:latest as postgres

FROM python:3.7

WORKDIR /app

COPY . .
COPY --from=postgres /usr/lib/postgresql/11/bin/pg_dump /app/bin/linux/pg_dump
COPY --from=postgres /usr/lib/x86_64-linux-gnu/libpq.so.5.11 /app/bin/linux/libpq.so.5
RUN pip install -r requirements.txt

CMD [ "python", "-u", "/app/main.py" ]
