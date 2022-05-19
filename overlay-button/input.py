# This was only possible because of this article: https://thehackerdiary.wordpress.com/2017/04/21/exploring-devinput-1/

import struct
import requests
import json
import os

# For details on how to set up your keypress generator with your EdgeCaster, please see the accomapnyng README.md

# You may need to change these variables if you use a button different than the one I tested with
# This is the device file for the button - see notes below to discover it
device = os.getenv("DEVICE_PATH")
print("Accessing the device at " + device)

# This is set for the IP used within Docker.
device_ip = '172.17.0.1'

# This is the Linux internal value for the key we're listening for. for the complete list of possible values, see:
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
key_pressed = 2

# We use these values below
channel_id = ''
channel_obj = ''
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
        ret = {"err_code": res.status_code, "err_message": + res.reason + '; ' + res.text}
    return ret

# Get all of the available data encoders
channels = get_json('http://' + device_ip + ':2020/v2/in_channels/')

if(len(channels["in_channels"]) > 0):
    print("Cycling through inputs...")
    for channel in channels["in_channels"]:
        channel_obj = get_json('http://' + device_ip + ':2020/v2/in_channels/' + str(channel["in_channel_id"]))

        # We choose the HDMI input here solely because it's the one we're using in this example.
        # But you can use any of the available and active input channels for this work. 
        if(channel_obj["video_input"]["value"] == 'input_hdmi'):
            channel_id = channel["in_channel_id"]

            # If there's no image already set, let's upload ours
            if(channel_obj["graphic_overlay"]["image_status"] == 'NO_IMAGE'):
                res = requests.post('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id) + '/overlay_graphic', files={'file': ('videon_logo.png', open('./videon_logo.png', 'rb'), 'image/png')})
                err = handleResponse(res)
                if(err != False):
                    print("Error updating input channel with Overlay data: " + err.err_code + ': ' + err.err_message)
                    exit

            # Let's go ahead and set some defaults for the image. For this, we'll just use the input image sized as-is and display it in the
            # lower right-hand corner of the display
            channel_obj["graphic_overlay"]["enable"] = False
            channel_obj["graphic_overlay"]["position"]["preset"]["value"] = 'BOTTOM_RIGHT'

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
        # We only want the key we pressed, so we need to make sure keypress[5] == key_pressed
        if(keypress[5] == key_pressed):
            if(overlay_enabled):
                print("We're DISabling the graphic (overlay_enabled = " + str(overlay_enabled) + ")")
                channel_obj["graphic_overlay"]["enable"] = False
                res = requests.put('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id), headers={"Content-Type": "application/json"}, json=channel_obj)
                overlay_enabled = False
            else:
                print("We're ENabling the graphic (overlay_enabled = " + str(overlay_enabled) + ")")
                channel_obj["graphic_overlay"]["enable"] = True
                res = requests.put('http://' + device_ip + ':2020/v2/in_channels/' + str(channel_id), headers={"Content-Type": "application/json"}, json=channel_obj)
                overlay_enabled = True
        else:
            print("Received a key press, but not the key we're listening for (", keypress[5], ")")
