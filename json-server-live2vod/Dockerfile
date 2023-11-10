FROM ubuntu:latest

# BUILD:
# docker build -t recorder_json .
# LAUNCH:
# docker run --name=recorder_json -v /data/local/internal_storage/savedvideo/Media/:/recordings -p9999:9999 recorder_json &
#
# See README.md for full explanations on the setup

# The LiveEdge Compute environment requires these user groups and permissions.
# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /json-server
COPY . /json-server
WORKDIR /json-server

RUN apt-get update
RUN apt-get install -y python3 ffmpeg

CMD python3 app.py
