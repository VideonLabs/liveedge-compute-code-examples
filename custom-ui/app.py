# Videon LiveEdge Compute Custom UI Example
#
# The LiveEdge Compute Platform allows you to completely customize the experience for your end users.
# Leveraging the Python Flask framework allows you to quickly build custom UIs that can provide 
# a more deeply branded or more controlled user experience.
#
# In this example, we will pre-load configuration files for a number of popular streaming sites
# to make it easy for a user to pop in their streaming ID and URL and get straight to broadcasting.
#
# For more details, see the tutorial here: [URL for TUTORIAL!!!]
#
# Note: All of the application code resides in this file for better accessibility and readability for all Python 
# skill levels. However, we suggest following best practices for code structure and readability for your own 
# production code. 

import os.path
from os import path
import videon_restful
import json
from flask import Flask, send_from_directory, Response, Request
from flask import render_template
app = Flask(__name__)

# The Videon RESTful server resides on the same device where this is running. Note, however,
# that this code could run from anywhere on the same network as the device. 
videon_ip = "127.0.0.1"

# Setup the configurations - these are defined as JSON files in the ./config directory.
print("Configuring profiles...")

# When you create a new profile, store it in the ./config/ directory and list the filename here. 
services = [
    "twitter.json",
    "twitch.json"
]

# We'll loop through the config files to extract the details and ensure each profile is setup properly
svc_config = {"vid_encoders": {}, "aud_encoders": {}}

for service in services:
    service = "./config/" + service
    print("Loading ", service)
    if path.exists(service):
        jsonfile = open(service, "r")

        try:
            print("Parsing JSON...")
            data = json.load(jsonfile)
            svc_config["vid_encoders"].update({data["video"]["name"]: data["video"]})
            svc_config["aud_encoders"].update({data["audio"]["name"]: data["audio"]})
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            print("Error decoding JSON for file " + service)

        jsonfile.close()

    else:
        print("Could not find path ", service)


print(svc_config)

print("Loading profiles from device...")

vid_encoders = {}
aud_encoders = {}

# The EdgeCaster saves the profiles we create on the device, so it's best to check
# whether they already exist before creating new ones. 
encoders = videon_restful.get_encoders(videon_ip)
for profile in encoders["vid_encoders"]:
    currEnc = videon_restful.get_vid_encoders_config(videon_ip, profile["vid_encoder_id"])
    vid_encoders[currEnc["name"]] = profile["vid_encoder_id"]
    
print("Vid Encoders found: \n", vid_encoders)

for profile in encoders["aud_encoders"]:
    currEnc = videon_restful.get_aud_encoders_config(videon_ip, profile["aud_encoder_id"])
    aud_encoders[currEnc["name"]] = profile["aud_encoder_id"]

print("Aud Encoders found: \n", aud_encoders)

# OK, let's see whether we need to create new profiles. Video first
for service in svc_config["vid_encoders"]:
    print("Checking service " + service)
    if(service in vid_encoders.keys()):
        print("Video encoder " + service + " is already configured")
    else:
        print("Creating new video encoder: " + service)
        cData = videon_restful.add_vid_encoder(videon_ip)
        print("cData: \n", cData)
        print("Updating the config data")
        data = videon_restful.put_vid_encoders_config(videon_ip, cData["id"], svc_config["vid_encoders"][service])
        print("Successfully configured " + service)

for service in svc_config["aud_encoders"]:
    print("Checking service " + service)
    if(service in aud_encoders.keys()):
        print("Audio encoder " + service + " is already configured")
    else:
        print("Creating new Audio encoder: " + service)
        cData = videon_restful.add_aud_encoder(videon_ip)
        print("Updating the config data")
        data = videon_restful.put_aud_encoders_config(videon_ip, cData["id"], svc_config["aud_encoders"][service])
        print("Successfully configured " + service)

# In order to stream video, we need to connect the video and audio profiles to an output stream. Let's get those streams now.
output_streams = videon_restful.get_out_streams(videon_ip)

# For the purposes of this example, we only care about the RTMP streams - used by all of the services we've configured - and the
# HTTP Pull stream, which we'll use to present a preview of the image on our interface. 
rtmp_ids = {}
http_pull_id = 0

for stream in output_streams["out_streams"]:
    if(stream["output_type"] == "rtmp"):
        # Creating the structure here for storing the stream information. Each dictionary will contain the information needed 
        # to properly connect an output stream to a profile.
        rtmp_ids[stream["out_stream_id"]] = {}
    if((stream["output_type"] == "http_pull") & (http_pull_id <= 0)):
        # We'll just grab the first http_pull ID we find - most devices will only have one.
        http_pull_id = 0

# With the video and audio sources configured, we can now allow the end user to select which services to stream to.
# The web application will present the user with a simple interface to request the information they need
# for each service and will automatically set up the stream. 

# We'll run an SPA off the root and use the rest of the routes for RESTful communication between the SPA and the app.
@app.route('/')
@app.route('/index')
def index():
    return render_template('customui.html')

#Since Flask is doing all the heavy lifting, it will also serve images and other static files. 
@app.route('/images/<path:path>')
def send_js(path):
    return send_from_directory('images', path)

@app.route('/streams/<int:id>', methods=['POST'])
def configure_stream(id):
    # Configures the given stream
    print("'sup")
    pass

# A convenience method to update the SPA
@app.route('/appstate', methods=['GET'])
@app.route('/appstate/', methods=['GET'])
def get_current_state():
    currState = {}
    currState["streams"] = rtmp_ids
    currState["services"] = svc_config
    return Response(json.dumps(currState, indent = 4), mimetype='application/json')

