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

# Install some default required packages
RUN apt-get install -y tzdata curl

# Make sure to set these values to your AWS credentials
ENV AWS_ACCESS_KEY_ID='[YOUR AWS ACCESS KEY ID]'
ENV AWS_SECRET_ACCESS_KEY='[YOUR AWS SECRET KEY]'
ENV AWS_REGION='[YOUR PREFERRED REGION (e.g. 'us-west-1')]'

# You can use these as-is or change them to fit your needs
ENV SERVER_PORT=5001

# The default Node packages in Ubuntu are not up to date with current releases, which 
# makes some of the libraries we use complain. So we're using NodeSource's ppa
# and installing from there

# This is a little more complicated on Ubuntu 20.04 because there are some dependency mismatches
# See https://stackoverflow.com/questions/55464934/npm-depends-node-gyp-3-6-2-but-it-is-not-going-to-be-installed
RUN apt-get install -y --allow-downgrades libssl1.1=1.1.1f-1ubuntu2
RUN apt-get install -y npm

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

RUN npm install

CMD node server.js