import evdev
import struct
import requests
import json
import os
import threading
from evdev import InputDevice, categorize, ecodes

# This is set for the IP used within Docker.
device_ip = '172.17.0.1'

# The duration in seconds for the insertion action to last
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
        ret = {"err_code": res.status_code, "err_message": res.reason + '; ' + res.text}
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
		res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders', headers={"Content-Type": "application/json"}, json={"codec": "scte35"})
		if(res.status_code == 201):
			json_data = json.loads(res.text)
			print(json_data)
			print(type(json_data))
			scte_id = json_data["id"]
			print("SCTE ID: " + str(scte_id))
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
	return scte_id

scteID = setupScte(device_ip, duration)

#Detect the usb device so that we can recognize key presses
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
	if "usb" in str(device.phys):

		if "input0" in str(device.phys):
			print(device.path, device.name, device.phys)
			deviceCap = device.capabilities()
			print(deviceCap)
			keyEventPath = device.path

dev = InputDevice(keyEventPath)

print(dev)

#Keep looping to detect key presses, taking the respective action for SCTE-35 splice markers
for event in dev.read_loop():
	if event.type == ecodes.EV_KEY:
		keyEvent = str(categorize(event))

        #Insert SCTE marker of 15 second duration
		if "(KEY_1), up" in keyEvent:
            print("Key 1 Hit!")
			duration = 15
			scteID=setupScte(device_ip, duration)
			res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/action/insert_splice', headers={"Content-Type": "application/json"}, json={})
			print(res)
			err = handleResponse(res)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Insert SCTE marker of 30 second duration
		if "(KEY_2), up" in keyEvent:
            print("Key 2 Hit!")
			duration = 30
			scteID=setupScte(device_ip, duration)
			res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/action/insert_splice', headers={"Content-Type": "application/json"}, json={})
			print(res)
			err = handleResponse(res)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Insert SCTE marker of 45 second duration
		if "(KEY_3), up" in keyEvent:
            print("Key 3 Hit!")
			duration = 45
			scteID=setupScte(device_ip, duration)
			res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/action/insert_splice', headers={"Content-Type": "application/json"}, json={})
			print(res)
			err = handleResponse(res)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #Insert SCTE marker of 60 second duration
		if "(KEY_4), up" in keyEvent:
            print("Key 4 Hit!")
			duration = 60
			scteID=setupScte(device_ip, duration)
			res = requests.post('http://' + device_ip + ':2020/v2/encoders/data_encoders/' + str(scteID) + '/action/insert_splice', headers={"Content-Type": "application/json"}, json={})
			print(res)
			err = handleResponse(res)
			if(err != False):
				print("Error setting splice: " + str(err["err_code"]) + ': ' + err["err_message"])
				exit

        #TODO: Initiate interrupt of splce marker
		if "(KEY_5), up" in keyEvent:
			print("Key 5 Hit!")

		print(categorize(event))
