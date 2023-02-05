####################################################################################################################
#
# Videon Edge App Custom Webserver Example
#
# In this example, we will pre-load configuration files for a number of popular streaming sites
# to make it easy for a user to pop in their streaming ID and URL and get straight to broadcasting.
#
# This webserver can be run on a Videon device, cloud server, or general computer - anything that can run a docker container
#
# Note: All of the application code resides in this file for better accessibility and readability for all Python 
# skill levels. However, we suggest following best practices for code structure and readability for your own 
# production code. 
#
#####################################################################################################################

# Make sure you grab the videon_cloud_restful.py helper library and place it in the same
# location as this script.
import videon_cloud_restful
import os
from os import path
import json

# For this example, we use Bottle to serve the application and CherryPy to manage the server, but other pure Python frameworks such as Flask
# Should work equally well.
import cherrypy as cp
import cherrypy_cors

import bottle
from bottle import Bottle, route, run, template, static_file, response, request

# The LiveEdge Cloud API server does not resides on the same device where this is running.
# For this example, we will hardcode the API URL
videon_cloud_url = "https://api.videoncloud.com/v1/"

# CherryPy requires this value to be an integer
listen_port = int(os.getenv("LISTENING_PORT"))

readyStreams = {}
currState = {}
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
    "youtube.json"
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
    # whether they already exist before creating new ones. Let's get the profiles from the device.
    encoders = videon_cloud_restful.get_encoders(videon_cloud_url)
    for profile in encoders["vid_encoders"]:
        currEnc = videon_cloud_restful.get_vid_encoders_config(videon_cloud_url, profile["vid_encoder_id"])
        vid_encoders[currEnc["name"]] = profile["vid_encoder_id"]

    for profile in encoders["aud_encoders"]:
        currEnc = videon_cloud_restful.get_aud_encoders_config(videon_cloud_url, profile["aud_encoder_id"])
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
            cData = videon_cloud_restful.add_vid_encoder(videon_cloud_url)
            print("CData: ")
            print(cData)
            data = videon_cloud_restful.put_vid_encoders_config(videon_cloud_url, cData["id"], svc_config[service]["video"])
            svc_config[service]["video_id"] = cData["id"]
        if(svc_config[service]["audio"]["name"] in aud_encoders.keys()):
            # It exists already, so let's grab the ID
            svc_config[service]["audio_id"] = aud_encoders[svc_config[service]["audio"]["name"]]
        else:
            # Doesn't exist - let's add the profile to the device.
            cData = videon_cloud_restful.add_aud_encoder(videon_cloud_url)
            data = videon_cloud_restful.put_aud_encoders_config(videon_cloud_url, cData["id"], svc_config[service]["audio"])
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

    # profile = svc_config[data["profile"]]

    # For simplicity's sake, we'll just take the first audio and video encoder we find, there should always be one of each created by the Videon device
    # TODO: Update this to load the YouTube audio encoder once LiveEdge Cloud supports adding encoders
    audio_id = 0
    video_id = 0
    for encoder in currState["encoders"]:
        if encoder["type"] == "audio":
            audio_id = encoder["id"]

    for encoder in currState["encoders"]:
        if encoder["type"] == "video":
            video_id = encoder["id"]

    for index, output in enumerate(currState["outputs"]):
        if currState["outputs"][index]["id"] == id:
            currState["outputs"][index]["config"]["sources"]["audio"][0] = audio_id
            currState["outputs"][index]["config"]["sources"]["video"][0] = video_id
            currState["outputs"][index]["config"]["service_data"] = "{'url': '" + rtmp_url + "'}"
            currState["outputs"][index]["config"]["service_value"] = "generic"

    outRes = videon_cloud_restful.put_out_streams(currState["token"], currState["device_guid"], currState["outputs_target_version"], currState["outputs"])

    readyStreams[id] = currState["rtmp_outputs"][id]

    return (outRes["return_code"], outRes["return_body"])

# We need to run this every time we want to update the state from the device. This builds the
# master "currState" object we use as a convenience method to work with the browser front end.
def updateState(token, device_guid):
    output_streams = {}
    shadows = videon_cloud_restful.send_shadow_get(token, device_guid)
    # Load in the respective shadows
    for shadow in shadows:
        match shadow["shadow_name"]:
            case "System":
                currState["system"] = shadow["reported"]["state"]
                currState["system_target_version"] = shadow["reported"]["current_version"]
            case "Inputs":
                currState["inputs"] = shadow["reported"]["state"]
                currState["inputs_target_version"] = shadow["reported"]["current_version"]
            case "Encoders":
                currState["encoders"] = shadow["reported"]["state"]
                currState["encoders_target_version"] = shadow["reported"]["current_version"]
            case "Outputs":
                currState["outputs"] = shadow["reported"]["state"]
                currState["outputs_target_version"] = shadow["reported"]["current_version"]

    # For the purposes of this example, we only care about the RTMP streams - used by all of the services we've configured
    rtmp_ids = {}

    for stream in currState["outputs"]:
        if(stream["type"] == "rtmp"):
            # Creating the structure here for storing the stream information. Each dictionary will contain the information needed 
            # to properly connect an output stream to a profile.
            rtmp_ids[stream["id"]] = stream["config"]

    # Load states of everything
    currState["token"] = token
    currState["device_guid"] = device_guid
    currState["rtmp_outputs"] = rtmp_ids
    currState["services"] = svc_config
    return currState


# We need to run this at least once to load the profiles up.
# updateProfiles()

##########################################################################################################################
#
# With the video and audio sources configured, we can now allow the end user to select which services to stream to.
# The web application will present the user with a simple interface to request the information they need
# for each service and will automatically set up the stream. 
#
# We'll run a Single Page Application (SPA) off the root and use the rest of the routes for API communication 
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
@app.route('/appstate/', method=['OPTIONS', 'POST'])
def get_current_state():
    data = request.json
    return updateState(data["token"], data["device_guid"])

# A simple POST call that tells the system to enable/disable the output streams
@app.route('/golive', method=['OPTIONS', 'POST'])
@app.route('/golive/', method=['OPTIONS', 'POST'])
def goLive():
    for id in readyStreams:
        if(readyStreams[id]["enable"]):
            readyStreams[id]["enable"] = False
        else:
            readyStreams[id]["enable"] = True
        print(readyStreams[id])
        res = videon_cloud_restful.put_out_streams_configs(videon_cloud_url, id, readyStreams[id])
        print("Reponse: ", res)
        if res["return_code"] != 200:
            response.status = res["return_code"] + ' ' + res["return_body"]
            return dict({"message": res["return_body"]})
    

# A simple POST call that tells the system to enable/disable the output streams
@app.route('/submitPAT/<token>', method=['OPTIONS', 'POST'])
def submitPAT(token):
    token_result = videon_cloud_restful.get_token_expiriation(token)
    if token_result:
        org_result = videon_cloud_restful.get_organizations(token)
        return org_result
    return token_result

# A simple POST call that tells the system to enable/disable the output streams
@app.route('/getDevices/', method=['OPTIONS', 'POST'])
def getDevices():
    data = request.json
    devices_result = videon_cloud_restful.get_devices(data["token"], data["org_guid"])
    return devices_result


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