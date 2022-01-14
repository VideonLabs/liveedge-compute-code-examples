FROM ubuntu

# These two lines are required for Docker containers running in LiveEdge Compute
RUN groupadd -g 3003 aid_inet && usermod -G nogroup -g aid_inet _apt
RUN groupadd -g 3004 net_raw && usermod -G net_raw root

# Be sure to replace these with the values for your S3 bucket
# You can obtain your AWS Access Key ID and secret either from
# your IAM settings on AWS, or from your ~/.aws/credentials file.

ENV AWS_ACCESS_KEY_ID=[REPLACE WITH AWS ACCESS KEY]]
ENV AWS_SECRET_ACCESS_KEY=[REPLACE WITH AWS SECRET KEY]
ENV SYNC_BUCKET=[REPLACE WITH the FOLDER NAME IN YOUR S3 Bucket]

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y inotify-tools curl unzip

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN chmod 755 ./monitor.sh

# Install rclone
RUN curl https://rclone.org/install.sh | bash

# Setup rclone
RUN rclone config create videon-aws-s3 s3 env_auth=true provider=aws

# Our script monitors the mapped directory for file closures, then runs rclone sync. 
CMD ./monitor.sh /app/media