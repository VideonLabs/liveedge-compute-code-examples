#!/usr/bin/env python3
#
# USB Button to Ad Insertion App
#
# Gather USB button signals and translate to SCTE35 ad insertion markers
#
# Procedure:
#   1.  Detect and connect to 5-key or 1-key USB devices
#   2.  Detect and setup SCTE35 data encoder on a local Videon
#   3.  Wait for button presses and translate to appropriate SCTE35 event
#

import evdev
import struct
import requests
import json
import os
import threading
from evdev import InputDevice, categorize, ecodes

# This is set for the IP used within Docker.
device_ip = '172.17.0.1'

# The duration in seconds for the insertion action to last (SETTING INITIAL VALUE)
duration = 10

# Create some placeholder variables
channel_id = ''
channel_obj = ''

scte_id = ''
scte_obj = ''


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
        ret = {"err_code": response.status_code, "err_message": response.reason + '; ' + response.text}
    return ret

def setupScte(device_ip, duration):
	# Set up the SCTE encoder
	# If there's already a SCTE Encoder, we need to use that or we get an error 500 at creation
	encoders = get_json('http://' + device_ip + ':2020/v2/encoders/data_encoders')
	scte_id = ''
	print("Looping through encoders")
	for encoder in encoders["data_encoders"]:
		print("CODEC: " + encoder["codec"])
		if(encoder["codec"] == "scte35"):
			scte_id = encoder["data_encoder_id"]
			print("Found SCTE ID: " + str(scte_id))
	# If no encoder is found, create one
	if(scte_id == ''):
		req = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders', headers={"Content-Type": "application/json"}, json={"codec": "scte35"})
		if(req.status_code == 201):
			json_data = json.loads(req.text)
			print(json_data)
			print(type(json_data))
			scte_id = json_data["id"]
			print("SCTE ID: " + str(scte_id))
		else:
			print("Call failed: " + str(req.status_code) + ": " + req.reason)

	# Get the SCTE Object
	scte_obj = get_json('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scte_id))

	# Clean up the scte_object
	del scte_obj["status"]
	del scte_obj["seconds_in_status"]
	del scte_obj["data_encoder_id"]
	scte_obj["name"] = "Insertion-Button"
	#del scte_obj["in_channel_in"]
	scte_obj["active"] = True

	print("SCTE ID: " + str(scte_id))
	
	# Update the duration to match our duration
	scte_obj["codec"]["scte35"]["splice_duration"] = duration * 1000
	tmpUrl = 'http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scte_id)
	req = requests.put(tmpUrl, headers={"Content-Type": "application/json"}, data=json.dumps(scte_obj))
	mRet = handleResponse(req)
	if(mRet != False):
		print("Error Updating SCTE encoder: " + json.dumps(mRet))
		print("URL: " + tmpUrl)
		print("Data: \n" + json.dumps(scte_obj))
	return scte_id

def scte_insert(device_ip, duration=120*1000):
    # Splice Insert with a preroll of 0 seconds and duration of 30 seconds (will be changed in the code)
	splice = {"splice_command":{"value":"splice_insert","splice_insert":{"preroll_time_msec":0,"duration_msec":30000}}}
	splice["splice_command"]["splice_insert"]["duration_msec"] = duration
	#splice["splice_command"]["splice_insert"]["active"] = "true"
	req = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/splice_commands', headers={"Content-Type": "application/json"}, json=splice)
	print(req)
	err = handleResponse(req)
	if(err != False):
		print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
		exit

scteID = setupScte(device_ip, duration)

#Detect the usb device so that we can recognize key presses
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

for device in devices:

	if "usb" in str(device.phys):

		if "input0" in str(device.phys):
			#print(device.path, device.name, device.phys)
			deviceCap = device.capabilities()
			#print(deviceCap)
			keyEventPath = device.path

dev = InputDevice(keyEventPath)

print(dev)	

# Splice Insert with a preroll of 0 seconds and duration of 30 seconds (This is changed depending on button press)
splice = {"splice_command":{"value":"splice_insert","splice_insert":{"preroll_time_msec":0,"duration_msec":30000}}}
# Time Signal
time_signal_start = {"splice_command":{"value":"time_signal","time_signal":{"preroll_time_msec": 200,"segmentation_descriptor":"021C435545494800008E7FCF0000A4CB8008080000000000000000340200"}}}
time_signal_end = {"splice_command":{"value":"time_signal","time_signal":{"preroll_time_msec": 200,"segmentation_descriptor":"0217435545494800008E7F9F08080000000000000000350200"}}}

#Keep looping to detect key presses, taking the respective action for SCTE-35 splice markers
for event in dev.read_loop():
	if event.type == ecodes.EV_KEY:
		keyEvent = str(categorize(event))
		
		print(keyEvent)

		#Insert SCTE marker of 120 second duration
		if "(KEY_KP1), up" in keyEvent:
			print("Key 1 Hit! 120 second Ad Break!!")
			duration= 120*1000
			scte_insert(device_ip, duration)

		#Insert SCTE marker of 120 second duration
		if "(KEY_1), up" in keyEvent:
			print("Key 1 Hit! 120 second Ad Break!!")
			duration= 120*1000
			splice["splice_command"]["splice_insert"]["duration_msec"]=duration 
			req = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/splice_commands', headers={"Content-Type": "application/json"}, json=splice)
			print(req)
			err = handleResponse(req)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Insert SCTE marker of 30 second duration
		if "(KEY_2), up" in keyEvent:
			print("Key 2 Hit! 30 Second Ad break")
			duration = 30*1000
			splice["splice_command"]["splice_insert"]["duration_msec"]=duration # if needed for passing to post add json.dumps(splice) in the request
			req = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/splice_commands', headers={"Content-Type": "application/json"}, json=splice)
			print(req)
			err = handleResponse(req)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Insert SCTE Time Signal Start 
		if "(KEY_3), up" in keyEvent:
			print("Key 3 Hit! SCTE Time Signal Start")
			req = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/splice_commands', headers={"Content-Type": "application/json"}, json=time_signal_start)
			print(req)
			err = handleResponse(req)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Insert SCTE Time Signal End
		if "(KEY_4), up" in keyEvent:
			print("Key 4 Hit! SCTE Time Signal End")
			req = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/splice_commands', headers={"Content-Type": "application/json"}, json=time_signal_end)
			print(req)
			err = handleResponse(req)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Initiate interrupt of ALL SPLICE COMMANDS
		if "(KEY_5), up" in keyEvent:
			print("Key 5 Hit! = Cancel all active splice commands!!")
			req = requests.delete('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/splice_commands/', headers={"Content-Type": "application/json"}, json={})
			print(req)
			err = handleResponse(req)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit
