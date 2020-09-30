FROM ubuntu:20.04
MAINTAINER jjpulidos98@gmail.com

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn -y

RUN mkdir /app
COPY requirements.txt requirements.txt
COPY flask-app /app/

RUN pip3 install -r requirements.txt
WORKDIR /app

CMD ["uvicorn", "app:app", "--reload"]
