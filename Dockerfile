FROM nvidia/cuda:10.1-devel-ubuntu18.04
MAINTAINER Satyalab, satya-group@lists.andrew.cmu.edu

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip

EXPOSE 9099
WORKDIR /gabriel-ikea
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["./main.py"]
