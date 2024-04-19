FROM python:3.8-slim-buster

RUN apt-get -y update; apt-get -y install curl git gcc g++

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

ENV FLASK_APP=app.py

#RUN pip3 install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


RUN apt-get -y update; apt-get -y install curl

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py", "--host", "0.0.0.0" ]