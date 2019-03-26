#!/bin/bash

set -e

docker run -it -v $(pwd)/bin:/pg_dump_bin postgres:latest bash -c 'cp /usr/lib/postgresql/11/bin/pg_dump /pg_dump_bin/linux/pg_dump && cp /usr/lib/x86_64-linux-gnu/libpq.so.5.11 /pg_dump_bin/linux/libpq.so.5'
