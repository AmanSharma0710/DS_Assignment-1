FROM ubuntu:20.04
RUN apt-get update
RUN apt install -y curl
RUN apt-get install -y docker.io
CMD ["/bin/bash"]