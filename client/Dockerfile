FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip install flask flask_cors
RUN pip install requests

COPY ./client ./client
COPY ./utils /utils
COPY ./config.json /config.json
COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8081

CMD ["python3", "client/client.py"]
# CMD ["/bin/bash"]