FROM python

# The LiveEdge Compute environment requires these user groups and permissions
# in order to allow access to certain outside servers. 
# These two lines *MUST* be included in your Dockerfile
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# First, set up the main directory structure
RUN mkdir /app
COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install -y python3 pip vim

# Install all of our Python dependencies
RUN pip install -r ./requirements.txt

ENV PYTHONUNBUFFERED=1

CMD python3 -u input.py