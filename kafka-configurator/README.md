# The Kafka Configurator
This simple code example demonstrates how to remotely command and control the EdgeCaster from a centralized location. Kafka is used in this example solely for its popularity - you can use practically any messaging queue so long as it has a client written in pure Python. 

Using a message queue in this way allows for asynchronous communication and event-driven interactions, both between a central administrative interface and amongst individual devices. 

This example assumes you have a Kafka broker running on your network that receives configuration messages from a central administrative system. If you don't already have access to a working Kafka broker, you can implement a simple broker and client in just a few minutes on your local machine by [following the Apache Kafka Quickstart](https://kafka.apache.org/quickstart). 

## Usage
Download the `videon_restful.py` helper library from this repository and place it in the same directory as this script. You'll need to run a Kafka broker and client to send messages to the queues this example listens on. Make sure you update the `kafka_server' variable with the address of your Kafka server.

**Note:** This example elides a lot of security best practices in order to present a clear example. We recommend following common best practices in securing your message queues and network cxommunications. 