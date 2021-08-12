# The remote configurator assumes you have a running instance
# of Kafka running somewhere. This application will subscribe
# to a topic and listen for configuration updates and act accordingly. 

# This will turn your EdgeCaster into an event driven client that
# responds quickly to commands posted to the message queue.

import videon_restful
import json
from kafka import KafkaConsumer, KafkaProducer

kafka_server = '192.168.86.31:9092' # Replace this with the IP / hostname of your Kafka server
config_topic = 'edgecaster-config' # You may consider creating topics for all EdgeCasters as well as on a per-name basis
registration_topic = 'edgecaster-register' # We use this in our example to notify our system that this EdgeCaster is online and ready 

size = 1000000

def startup():
    # Let's get some information about the device and register it as active on the system
    props = videon_restful.get_system_properties('127.0.0.1')
    producer = KafkaProducer(bootstrap_servers=kafka_server, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    producer.send(registration_topic, props)
    producer.flush() #Since send() is async, we flush to get the value to the server immediately. 

def consume():
    # Listens on the given topic for messages and passes them to the handler function.
    consumer = KafkaConsumer(bootstrap_servers=kafka_server)  #, value_deserializer=msgpack.loads
    consumer.subscribe([config_topic])
    for msg in consumer:
        #assert isinstance(msg.value, dict)
        process_message(msg.value)

def process_message(msg):
    # In this *extremely* simple example, we will simply grab any messages with a key 'new-config' and implement the JSON.
    # The message values MUST be formatted following the system properties. as seen in the API docs
    # TODO: Add security to this
    if msg.key == 'new-config':
        print('Updating device configuration...')
        videon_restful.put_system_properties(msg.value)
    # Add elifs to handle other message types
    else:
        print('Unhandled message: ' + msg.key)

if __name__ == '__main__':
    startup()
    consume()