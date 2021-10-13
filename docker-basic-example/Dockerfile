FROM ubuntu:latest

# The LiveCompute environment requires these user groups and permissions
# in order to allow access to certain outside servers. 
# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /streaming
COPY . /streaming
WORKDIR /streaming
RUN rm -rf node_modules

# Need to install SSH first
RUN apt-get update

# Ubuntu may prompt for input if these values aren't set, slowing the build process.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

# Running this separatel to handle an ionput issue when installing tzdata
RUN apt-get install -y tzdata

# This environment variable is used by our Node script to determine the port our server run on
ENV LISTENING_PORT=8888

# Our application requires these three programs to run
RUN apt-get install -y npm nodejs

# Install all of our Node dependencies
RUN npm install

# When you call `docker run`, this is the command that docker will issue to start up the container.
CMD node index.js