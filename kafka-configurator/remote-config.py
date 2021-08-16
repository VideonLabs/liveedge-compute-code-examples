#################################################################################
# 
# The Kafka Configurator
#
# This code example demonstrates how to remotely command and control the EdgeCaster
# from a centralized location. Kafka is used in this example solely for its 
# popularity - you can use practically any messaging queue so long as it has a 
# client written in pure Python. 
#
# Using a message queue in this way allows for asynchronous communication and 
# event-driven interactions, both between a central administrative interface
# and amongst individual devices. 
#
# This example assumes you have a Kafka broker running on your network that receives
# configuration messages from a central administrative system. Implementing that
# is left as an exercise for the reader.
#
#################################################################################

# Make sure you grab the videon_restful.py helper library and place it in the same
# location as this script.
import videon_restful
import json
from kafka import KafkaConsumer, KafkaProducer

kafka_server = '[REPLACE WITH YOUR KAFKA SERVER ADDRESS]' # Replace this with the IP / hostname of your Kafka server
config_topic = 'edgecaster-config' # You may consider creating topics for all EdgeCasters as well as on a per-name basis
registration_topic = 'edgecaster-register' # We use this in our example to notify our system that this EdgeCaster is online and ready 

size = 1000000
videon_ip = ''

def startup():
    # Let's get some information about the device and register it as active on the system.
    # The get_system_properties call returns just about everything we need to know how to 
    # access this particular device, so we can just send the raw JSON output back to the
    # Kafka broker.
    global videon_ip
    props = videon_restful.get_system_properties('127.0.0.1')
    if "ip_address" in props:
        videon_ip = props["ip_address"]
    else:
        videon_ip = "127.0.0.1"
    producer = KafkaProducer(bootstrap_servers=kafka_server, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    producer.send(registration_topic, props)
    producer.flush() #Since send() is async, we flush to get the value to the server immediately. 

def consume():
    # Listens on the given topic for messages and passes them to the handler function.
    consumer = KafkaConsumer(bootstrap_servers=kafka_server)  #, value_deserializer=msgpack.loads
    consumer.subscribe([config_topic])
    for msg in consumer:
        process_message(msg.value)

def process_message(msg):
    # In this *extremely* simple example, we will assume Kafka messages are formatted with a "command key" that
    # defines the function the device should carry out. In this case, we'll implement two functions - one that 
    # updates the device's configuration and one that creates a new video profile.
    #
    # You can get rather creative here to suit your needs.
    if msg.key == 'update-config':
        print('Updating device configuration...')
        videon_restful.put_system_properties(videon_ip, msg.value)
    elif msg.key == 'add-vid-profile':
        print('Received a new video encoding profile...')
        videon_restful.put_vid_encoders_config(videon_ip, msg.value)

    # Add elifs to handle other message types
    else:
        print('Unhandled message: ' + msg.key)

if __name__ == '__main__':
    startup()
    consume()