FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip install flask flask_cors

RUN mkdir /server
COPY . /server
WORKDIR /server

EXPOSE 12345

CMD ["python3", "server.py"]