FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y ca-certificates curl gnupg lsb-release
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

RUN pip install --upgrade pip

COPY ./loadbalancer ./loadbalancer
COPY ./utils /utils
COPY ./requirements.txt /requirements.txt
COPY ./config.json /config.json

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "loadbalancer/loadbalancer.py"]
