####################################################################################################################
#
# Videon LiveEdge Compute Custom UI Example
#
# The LiveEdge Compute Platform allows you to completely customize the experience for your end users.
#
# In this example, we will pre-load configuration files for a number of popular streaming sites
# to make it easy for a user to pop in their streaming ID and URL and get straight to broadcasting.
#
# Note: All of the application code resides in this file for better accessibility and readability for all Python 
# skill levels. However, we suggest following best practices for code structure and readability for your own 
# production code. 
#
#####################################################################################################################

# Make sure you grab the videon_restful.py helper library and place it in the same
# location as this script.
import videon_restful
import os
from os import path
import json

# For this example, we use Bottle to serve the application and CherryPy to manage the server, but other pure Python frameworks such as Flask
# Should work equally well.
import cherrypy as cp
import cherrypy_cors

import bottle
from bottle import Bottle, route, run, template, static_file, response, request

# The LiveEdge RESTful API erver resides on the same device where this is running.
# Since this is running in a container, we'll use an environment variable
videon_ip = os.getenv("HOST_IP_ADDRESS")

# CherryPy requires this value to be an integer
listen_port = int(os.getenv("LISTENING_PORT"))

readyStreams = {}
previewEnabled = False

######################################################################################################
#
# Application specific helper code code
#
# For this use case, we created configuration files with the audio and video details for each of the 
# services this application will support. There should be one file for each service covered (i.e. one 
# for Twitter, one for Twitch, one for Faceboo, etc.). See the files in the `config` directory for the 
# format. 
services = [
    "youtube.json",
    "facebook.json",
    "twitch.json"
]

# Setup the configurations - these are defined as JSON files in the ./config directory.
# We'll loop through the config files to extract the details and ensure each profile is setup properly
svc_config = {}

for service in services:
    service = "./config/" + service
    print("Loading ", service)
    if path.exists(service):
        jsonfile = open(service, "r")
        try:
            data = json.load(jsonfile)
            svc_config[data["name"]] = data
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            print("Error decoding JSON for file " + service)

        jsonfile.close()

    else:
        print("Could not find path ", service)

#
######################################################################################################



# The device is capable of storing several profiles containing the audio and configuration details
# for each stream type. For this use case, we stored the values recommended by the stream distributors
# in the external configuration files we just loaded. 
#
# If this is the first time this application is running, then we need to create those profiles on the device. 

def updateProfiles():
    vid_encoders = {}
    aud_encoders = {}

    # The EdgeCaster saves the profiles we create on the device, so it's best to check
    # whether they already exist before creating new ones. Let's get the profiles on the box.
    encoders = videon_restful.get_encoders(videon_ip)
    for profile in encoders["vid_encoders"]:
        currEnc = videon_restful.get_vid_encoders_config(videon_ip, profile["vid_encoder_id"])
        vid_encoders[currEnc["name"]] = profile["vid_encoder_id"]

    for profile in encoders["aud_encoders"]:
        currEnc = videon_restful.get_aud_encoders_config(videon_ip, profile["aud_encoder_id"])
        aud_encoders[currEnc["name"]] = profile["aud_encoder_id"]

    print("Videos")
    print(vid_encoders)
    print("Audios")
    print(aud_encoders)

    # OK, let's see whether we need to create new profiles. Video first
    for service in svc_config.keys():
        print("Service: " + service)
        if(svc_config[service]["video"]["name"] in vid_encoders.keys()):
            # It exists already, so let's grab the ID
            svc_config[service]["video_id"] = vid_encoders[svc_config[service]["video"]["name"]]
        else:
            # Doesn't exist - let's add the profile to the device. 
            cData = videon_restful.add_vid_encoder(videon_ip)
            print("CData: ")
            print(cData)
            data = videon_restful.put_vid_encoders_config(videon_ip, cData["id"], svc_config[service]["video"])
            svc_config[service]["video_id"] = cData["id"]
        if(svc_config[service]["audio"]["name"] in aud_encoders.keys()):
            # It exists already, so let's grab the ID
            svc_config[service]["audio_id"] = aud_encoders[svc_config[service]["audio"]["name"]]
        else:
            # Doesn't exist - let's add the profile to the device.
            cData = videon_restful.add_aud_encoder(videon_ip)
            data = videon_restful.put_aud_encoders_config(videon_ip, cData["id"], svc_config[service]["audio"])
            svc_config[service]["audio_id"] = cData["id"]
    print("SERVICES: \n")
    print(svc_config)

# This accepts the RTMP URL and stream key from our web application and configures the associated
# RTMP stream accordingly. Since we expect there to be some set up before going live,
# We simply set up the streams here, but don't enable them.
def configStream(id, data):
    return_code = ''
    return_msg = ''
    # Check for a trailing slash in the URL
    if data["stream_url"][len(data["stream_url"])-1] != '/':
        data["stream_url"] = data["stream_url"] + "/"

    # This is how many services set up their RTMP input streams - streaming URL + stream key.
    # Note, this may not work for all such services.
    rtmp_url = data["stream_url"] + data["stream_key"]

    profile = svc_config[data["profile"]]

    stream_obj = videon_restful.get_out_streams_configs(videon_ip, id)

    stream_obj["audio_sources"]["audio_source_ids"] = [profile["audio_id"]]
    stream_obj["video_sources"]["video_source_ids"] = [profile["video_id"]]
    stream_obj["output_type"]["rtmp"]["service"]["data"] = "{'url': '" + rtmp_url + "'}"

    outRes = videon_restful.put_out_streams_configs(videon_ip, id, stream_obj)

    readyStreams[id] = stream_obj

    return (outRes["return_code"], outRes["return_body"])

# We need to run this every time we want to update the state from the device. This builds the
# master "currState" object we use as a convenience method to work with the browser front end.
def updateState():
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
            rtmp_ids[stream["out_stream_id"]] = videon_restful.get_out_streams_configs(videon_ip, stream["out_stream_id"])
        elif(stream["output_type"] == "thumbnail"):
            # Need to turn on the thumbnail JPG previewer
            if(not previewEnabled):
                res = videon_restful.get_out_streams_configs(videon_ip, stream["out_stream_id"])
                if(not res["enable"]):
                    res["enable"] = True
                    videon_restful.put_out_streams_configs(videon_ip, stream["out_stream_id"], res)



    # We want to load the input streams to make sure we're getting a signal.

    input_channels = {}
    input_streams = videon_restful.get_in_channels(videon_ip)

    for stream in input_streams["in_channels"]:
        input_channels[stream["in_channel_id"]] = videon_restful.get_in_channel_config(videon_ip, stream["in_channel_id"])


    currState = {}
    currState["system"] = videon_restful.get_system_properties(videon_ip)
    currState["inputs"] = input_channels
    currState["streams"] = rtmp_ids
    currState["services"] = svc_config
    return currState


# We need to run this at least once to load the profiles up.
updateProfiles()

##########################################################################################################################
#
# With the video and audio sources configured, we can now allow the end user to select which services to stream to.
# The web application will present the user with a simple interface to request the information they need
# for each service and will automatically set up the stream. 
#
# We'll run a Single Page Application (SPA) off the root and use the rest of the routes for RESTful communication 
# between the SPA and the app.
#
##########################################################################################################################3

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


app = Bottle()

@app.route('/', method=['OPTIONS', 'GET'])
@app.route('/index', method=['OPTIONS', 'GET'])
def index():
    return template('customui.html')

#Since Bottle is doing all the heavy lifting, it will also serve images and other static files. 
@app.route('/static/<filepath:path>', method=['OPTIONS', 'GET'])
def serve_static(filepath):
    return static_file(filepath, root='static/')

@app.route('/streams/<id:int>', method=['POST'])
def configure_stream(id):
    # Configures the given stream
    print("Configuring stream ID: ", id)
    try:
        data = request.json
        (r_status, r_msg) = configStream(id, data)
        response.status = "201 Updated"
        return
    except ValueError:
        print("Invalid JSON:\n")
        print(request.body.read())
        return bottle.HTTPResponse(body=r_msg, status=r_status)

# A convenience method to update the SPA
@app.route('/appstate', method=['OPTIONS', 'GET'])
@app.route('/appstate/', method=['OPTIONS', 'GET'])
def get_current_state():
    return updateState()

# A simple POST call - not exactly RESTful - that tells the system to enable/diable the output streams
@app.route('/golive', method=['OPTIONS', 'POST'])
@app.route('/golive/', method=['OPTIONS', 'POST'])
def goLive():
    for id in readyStreams:
        if(readyStreams[id]["enable"]):
            readyStreams[id]["enable"] = False
        else:
            readyStreams[id]["enable"] = True
        print(readyStreams[id])
        res = videon_restful.put_out_streams_configs(videon_ip, id, readyStreams[id])
        print("Reponse: ", res)
        if res["return_code"] != 200:
            response.status = res["return_code"] + ' ' + res["return_body"]
            return dict({"message": res["return_body"]})

app.install(EnableCors())

#Run through CherryPy to get multithreading / true WSGI support
cherrypy_cors.install()
cp.tree.graft(app, '/')
cp.config.update({
    'server.socket_port': listen_port,
    'server.socket_host': "0.0.0.0",
    '/': {
        'cors.expose.on': True,
    }
})

cp.engine.signals.subscribe() # optional
cp.engine.start()
cp.engine.block()