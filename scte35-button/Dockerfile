# Docker 
FROM ubuntu:latest

# The LiveCompute environment requires these user groups and permissions
# in order to allow access to certain outside servers. 

# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /app
COPY . /app
WORKDIR /app

RUN rm -rf node_modules

# Need to install SSH first
RUN apt-get update

# Ubuntu may prompt for input if these values aren't set, slowing the build process.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

RUN apt-get install -y tzdata nodejs npm

RUN npm install

CMD node server.js