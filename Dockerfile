FROM python:3-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY main.py /app

CMD [ "python", "-u", "/app/main.py" ]
