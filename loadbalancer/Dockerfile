FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y ca-certificates curl gnupg lsb-release
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https ://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources .list.d/docker.list > /dev/null
RUN sudo apt-get install docker-ce docker-ce-cli containerd.io
RUN pip install --upgrade pip

COPY ./loadbalancer ./loadbalancer
COPY ./utils /utils
COPY ./requirements.txt /requirements.txt
COPY ./config.json /config.json

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "loadbalancer/loadbalancer.py"]
