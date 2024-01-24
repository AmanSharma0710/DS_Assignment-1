FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip install requests

COPY ./client.py ./client.py

EXPOSE 8081

CMD ["python3", "client.py"]
# CMD ["/bin/bash"]