FROM ubuntu:latest

# The LiveEdge Compute environment requires these user groups and permissions
# in order to allow access to certain outside servers. 
# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /customui
COPY . /customui
WORKDIR /customui

# Need to install SSH first
RUN apt-get update

# Ubuntu may prompt for input if these values aren't set, slowing the build process.
#ARG DEBIAN_FRONTEND=noninteractive
#ENV TZ=America/Los_Angeles

# Running this separately to handle an input issue when installing tzdata
#RUN apt-get install -y tzdata

# This environment variable is used by our script to determine the port our server runs on
ENV LISTENING_PORT=8888

# There is no platform independent way to easily get the host address to access the LiveEdge Compute API.
# However, this is the default used by Docker in Linux, so we'll set it here. 
ENV HOST_IP_ADDRESS="172.17.0.1"

# Our application requires these two programs to run
RUN apt-get install -y python3 pip

# Install all of our Python dependencies
RUN pip install -r ./requirements.txt

# When you call `docker run`, this is the command that docker will issue to start up the container.
CMD python3 app.py