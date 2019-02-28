FROM python:3-alpine

WORKDIR /app

COPY main.py /app
RUN pip install hvac pymongo boto3

CMD [ "python", "-u", "/app/main.py" ]
