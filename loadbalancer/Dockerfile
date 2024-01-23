FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get update
RUN apt-get install -y docker.io
RUN apt-get -y install sudo
RUN pip install --upgrade pip

COPY ./loadbalancer ./loadbalancer
COPY ./utils /utils
COPY ./requirements.txt /requirements.txt
COPY ./config.json /config.json

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "loadbalancer/loadbalancer.py"]
