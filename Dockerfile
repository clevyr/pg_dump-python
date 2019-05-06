FROM postgres:11-alpine as postgres

FROM python:3.7-alpine

WORKDIR /app

COPY . .
COPY --from=postgres /usr/local/bin/pg_dump /app/bin/linux/pg_dump
COPY --from=postgres /usr/local/lib/libpq.so.5.11 /app/bin/linux/libpq.so.5
RUN pip install -r requirements.txt

ENV LD_LIBRARY_PATH=/app/bin/linux

CMD [ "python", "-u", "/app/main.py" ]
