# Use an external button emulating a keyboard press to insert a SCTE-35 marker and SMPTE 1080 color bars for a set duration.
import struct
import requests
import json
import os
import threading

# For details on how to set up your keypress generator with your EdgeCaster, please see the accomapnyng README.md

# You may need to change these variables if you use a button different than the one we tested with
# This is the device file for the button - see notes below to discover it
device = os.getenv("DEVICE_PATH")
print("Accessing the device at " + device)

# This is set for the IP used within Docker.
device_ip = '172.17.0.1'

# This is the Linux internal value for the key we're listening for. for the complete list of possible values, see:
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
key_pressed = 2

# The duration in seconds for the insertion action to last
duration = 10 



# Create some placeholder variables
channel_id = ''
channel_obj = ''

scte_id = ''
scte_obj = ''
overlay_enabled = False

# Helper function for GETting API endpoints
def get_json(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print("Error: " + str(r.status_code) + " " + str(r.text))
        return {"return_code": str(r.status_code), "return_body": str(r.text)}
    json_data = json.loads(r.text)
    return json_data

#Helper function to handling HTTP errors
def handleResponse(response):
    # Only reports an error if we get anything other than an OK error.
    ret = False
    if((int(response.status_code/100) % 10) != 2):
        ret = {"err_code": res.status_code, "err_message": res.reason + '; ' + res.text}
    return ret

# Stops the overlay. the SCTE35 will be allowed to run its course based on the duration for which it was set
def stop_overlay():
    global overlay_enabled
    print("We're DISabling the graphic (overlay_enabled = " + str(overlay_enabled) + ")")
    channel_obj["graphic_overlay"]["enable"] = False
    res = requests.put('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id), headers={"Content-Type": "application/json"}, json=channel_obj)
    overlay_enabled = False

# Triggers the SMPTE color bars and SCTE35 insertion.
def start_overlay():
    global overlay_enabled
    print("We're ENabling the graphic (overlay_enabled = " + str(overlay_enabled) + ")")
    channel_obj["graphic_overlay"]["enable"] = True

    # Start the SCTE Insert
    res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scte_id) + '/action/insert_splice', headers={"Content-Type": "application/json"}, json={})

    # Start the overlay
    res = requests.put('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id), headers={"Content-Type": "application/json"}, json=channel_obj)
    err = handleResponse(res)
    if(err != False):
        print("Error setting splice: " + err.err_code + ': ' + err.err_message)
        exit

    overlay_enabled = True

# We need to set up both the overlay image and the SCTE35 data encoder.

# Set up the overlay image on the input channel
# First, get all of the available data encoders
channels = get_json('http://' + device_ip + ':2020/v2/in_channels/')

# Then, find the one we want to use
if(len(channels["in_channels"]) > 0):
    for channel in channels["in_channels"]:
        channel_obj = get_json('http://' + device_ip + ':2020/v2/in_channels/' + str(channel["in_channel_id"]))

        # We choose the HDMI input here solely because it's the one we're using in this example.
        # But you can use any of the available and active input channels for this work. 
        if(channel_obj["video_input"]["value"] == 'input_hdmi'):
            channel_id = channel["in_channel_id"]

            # Let's upload our image
            res = requests.post('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id) + '/overlay_graphic', files={'file': ('smpte_color_bars.png', open('./smpte_color_bars.png', 'rb'), 'image/png')})
            err = handleResponse(res)
            if(err != False):
                print("Error updating input channel with Overlay data: " + err.err_code + ': ' + err.err_message)
                exit

            # Let's go ahead and set some defaults for the image. For this, we'll just use the input image sized as-is and display it in the
            # lower right-hand corner of the display
            channel_obj["graphic_overlay"]["enable"] = False
            channel_obj["graphic_overlay"]["position"]["preset"]["value"] = 'FULLSCREEN'

            res = requests.put('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id), headers={"Content-Type": "application/json"}, json=channel_obj)
            err = handleResponse(res)
            if(err != False):
                print("Error updating input channel with Overlay data: " + err.err_code + ': ' + err.err_message)
                exit
            overlay_enabled = False
            break
else:
    print("No input channels found. Are you sure you're connected to a device? Exiting.")
    exit()


# Set up the SCTE encoder
# If there's already a SCTE Encoder, we need to use that or we get an error 500 at creation
encoders = get_json('http://' + device_ip + ':2020/v2/encoders/data_encoders')
print("Looping through encoders")
for encoder in encoders["data_encoders"]:
    print("CODEC: " + encoder["codec"])
    if(encoder["codec"] == "scte35"):
        scte_id = encoder["data_encoder_id"]
        print("Found SCTE ID: " + str(scte_id))

# If no encoder is found, create one
if(scte_id == ''):
    res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders', headers={"Content-Type": "application/json"}, json={"codec": "scte35"})
    if(res.status_code == 201):
        json_data = json.loads(res.text)
        scte_id = json_data.id
        print("SCTE ID: " + scte_id)
    else:
        print("Call failed: " + str(res.status_code) + ": " + res.reason)

# Get the SCTE Object
scte_obj = get_json('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scte_id))

# Clean up the scte_object
del scte_obj["status"]
del scte_obj["seconds_in_status"]
del scte_obj["data_encoder_id"]
scte_obj["name"] = "Insertion-Button"

# Update the duration to match our duration
scte_obj["codec"]["scte35"]["splice_duration"] = duration * 1000
tmpUrl = 'http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scte_id)
res = requests.put(tmpUrl, headers={"Content-Type": "application/json"}, data=json.dumps(scte_obj))
mRet = handleResponse(res)
if(mRet != False):
    print("Error Updating SCTE encoder: " + json.dumps(mRet))
    print("URL: " + tmpUrl)
    print("Data: \n" + json.dumps(scte_obj))
    

# Open the device for listening
f = open( device, "rb" ); # Open the device file handle in read-binary mode

# Basically a server to listen for keypresses
while 1:
    data = f.read(24)

    # This unpacks the binary struct into a tuple. See the README.md for details on how this struct is formatted
    keypress = struct.unpack('4IHHI', data)

    # keypress[0..3] contains the timestamp values for the events - we don't use them here. 
    # We're looking only for keyboard presses, which should correspond to keypress[4] == 1
    # We only want to do it when the key is actually pressed, not lifted, so we're looking at the value keypress[6] == 1
    if((keypress[4] == 1) and (keypress[6] == 1)):
        if(keypress[5] == key_pressed):
            if(overlay_enabled):
                print("Overlay is enabled - not restarting.")
            else:
                start_overlay()
                threading.Timer(duration, stop_overlay).start()
        else:
            print("Received a key press, but not the key we're listening for (", keypress[5], ")")







