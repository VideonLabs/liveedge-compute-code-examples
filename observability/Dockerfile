FROM ubuntu

# These two lines are required for Docker containers running in LiveEdge Compute
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y wget 

# We download Prometheus directly from their GitHub repo. 
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.32.1/prometheus-2.32.1.linux-arm64.tar.gz
RUN tar xvfz prometheus-2.32.1.linux-arm64.tar.gz

CMD ./prometheus-2.32.1.linux-arm64/prometheus --config.file=/app/prometheus.yml