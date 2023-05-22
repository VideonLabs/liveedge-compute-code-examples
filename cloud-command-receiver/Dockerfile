FROM ubuntu:latest

# The LiveEdge Compute environment requires these user groups and permissions
# in order to allow access to certain outside servers. 
# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /cloud-reciever
COPY . /cloud-reciever
WORKDIR /cloud-reciever
RUN rm -rf node_modules

# Need to install SSH first
RUN apt-get update

# Ubuntu may prompt for input if these values aren't set, slowing the build process.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Denver

# Running this separately to handle an input issue when installing tzdata
RUN apt-get install -y tzdata

# This environment variable is used by our Node script to determine the port our server runs on
ENV LISTENING_PORT=8882

# There is no platform independent way to easily get the host address to access the LiveEdge Compute API.
# However, this is the default used by Docker in Linux, so we'll set it here. 
ENV HOST_IP_ADDRESS="172.17.0.1"

# Our application requires these two programs to run
RUN apt-get install -y npm nodejs

# Install all of our Node dependencies
RUN npm install

# When you call `docker run`, this is the command that docker will issue to start up the container.
CMD node index.js