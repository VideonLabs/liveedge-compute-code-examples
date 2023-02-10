FROM ubuntu:latest

# The LiveEdge® Compute environment requires these user groups and permissions
# in order to allow access to certain outside servers. 
# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /cloud-api-example
COPY . /cloud-api-example
WORKDIR /cloud-api-example

# Need to install SSH first
RUN apt-get update

# Ubuntu may prompt for input if these values aren't set, slowing the build process.
#ARG DEBIAN_FRONTEND=noninteractive
#ENV TZ=America/Denver

# Running this separately to handle an input issue when installing tzdata
#RUN apt-get install -y tzdata

# This environment variable is used by our script to determine the port our server runs on
ENV LISTENING_PORT=8888

# Our application requires these two programs to run
RUN apt-get install -y python3 pip

# Install all of our Python dependencies
RUN pip install -r ./requirements.txt

# When you call `docker run`, this is the command that docker will issue to start up the container.
CMD python3 app.py