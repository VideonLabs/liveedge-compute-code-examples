#################################################################################
#
# videon_cloud_restful.py
#
# This is a simple set of helper functions to make it easier to call the LiveEdge® 
# CLOUD REST API controlling an enrolled Videon hardware device. 
#
# This helper may not have every possible API call since it serve as mainly 
# an example to expand on.
# 
#################################################################################

import requests
import json
import sys
import os
import time

# LiveEdge® CLOUD REST API urls and endpoints
cloud_api_url = "https://api.videoncloud.com/v1/"
cloud_personal_access_token_endpoint = "pats/"
cloud_orgs_endpoint = "orgs/"
cloud_devices_endpoint = "devices/"
cloud_shadow_endpoint = "/shadows/"
cloud_shadow_command_endpoint = "/shadows/commands/"
system_shadow = "System"
inputs_shadow = "Inputs"
encoders_shadow = "Encoders"
outputs_shadow = "Outputs"

# Helper function to confirm PAT and return expiration date
# This function expects a Personal Access Token that is generated from the LiveEdge® CLOUD platform
#   and returns either the expiration date of the token if valid or "Token not found" if not valid.
# Constructed endpoint: https://api.videoncloud.com/v1/pats/
def get_token_expiration(cloud_api_url, token):
    r = requests.get(cloud_api_url + cloud_personal_access_token_endpoint, headers={"Authorization":"PAT " + token})
    if r.status_code != requests.codes.ok:
        sys.exit("Status code = " + str(r.status_code) + "\nMessage = " + str(json.loads(r.text)["message"]))
    else:
        tokens = json.loads(r.text)["personal_access_tokens"]
        for token_found in tokens:
            if token_found["token_prefix"] == token[0 : 5]:
                res = requests.get(cloud_api_url + cloud_personal_access_token_endpoint + token_found["token_guid"], headers={"Authorization":"PAT " + token})
                return res
    return "Token not found"

# Helper function to get a list of orgs associated with a token GUID
# This function expects a valid LiveEdge® CLOUD Personal Access Token
#   and returns a list of organizations associated with that PAT
# Constructed endpoint: https://api.videoncloud.com/v1/orgs/
def get_organizations(cloud_api_url, token):
    r = requests.get(cloud_api_url + cloud_orgs_endpoint, headers={"Authorization":"PAT " + token})
    if r.status_code != requests.codes.ok:
        sys.exit("Status code = " + str(r.status_code) + "\nMessage = " + str(json.loads(r.text)["message"]))

    orgs = r.json()["orgs"]
    pagination_token = r.json()["pagination_token"]
    while pagination_token:
        r = requests.get(cloud_api_url + cloud_orgs_endpoint, params={"pagination_token": pagination_token}, headers={"Authorization":"PAT " + token})
        if r.status_code != requests.codes.ok:
            sys.exit("Status code = " + str(r.status_code) + "\nMessage = " + str(json.loads(r.text)["message"]))
        orgs += r.json()["orgs"]
        pagination_token = r.json()["pagination_token"]
    return orgs

# Helper function to get a list of devices associated with an org GUID
# This function expects a valid LiveEdge® CLOUD Personal Access Token and organization GUID
#   and returns a list of devices associated with that organization that the user has access to
# Constructed endpoint: https://api.videoncloud.com/v1/devices/
def get_devices(cloud_api_url, token, org_guid):
    payload = {"org_guid" : org_guid}
    r = requests.get(cloud_api_url + cloud_devices_endpoint, headers={"Authorization":"PAT " + token}, params=payload)
    if r.status_code != requests.codes.ok:
        sys.exit("Status code = " + str(r.status_code) + "\nMessage = " + str(json.loads(r.text)["message"]))
    
    devices = r.json()["devices"]
    pagination_token = r.json()["pagination_token"]
    while pagination_token:
        payload = {"org_guid" : org_guid, "pagination_token": pagination_token}
        r = requests.get(cloud_api_url + cloud_devices_endpoint, headers={"Authorization":"PAT " + token}, params=payload)
        if r.status_code != requests.codes.ok:
            sys.exit("Status code = " + str(r.status_code) + "\nMessage = " + str(json.loads(r.text)["message"]))
        devices += r.json()["devices"]
        pagination_token = r.json()["pagination_token"]
    return devices

# Helper function for getting device settings from the Cloud API
# This function expects a valid LiveEdge® CLOUD Personal Access Token and device GUID
#   and returns the full shadow of that device
# Constructed endpoint: https://api.videoncloud.com/v1/{device_guid}/shadows
def send_device_shadows_get(cloud_api_url, token, device_guid):
    # Send shadow get
    r = requests.get(cloud_api_url + cloud_devices_endpoint + device_guid + cloud_shadow_endpoint, headers={"Authorization":"PAT " + token})
    if r.status_code != 200 and r.status_code != 202:
        sys.exit("status code = " + str(r.status_code))
    return json.loads(r.text)["shadows"]

# Helper function for getting device settings for a specific shadow from the Cloud API
# This function expects a valid LiveEdge® CLOUD Personal Access Token, device GUID, and desired shadow name
#   and returns the specified shadow of that device
# Constructed endpoint: https://api.videoncloud.com/v1/{device_guid}/shadows
def send_shadow_get(cloud_api_url, token, device_guid, shadow_name):
    data = {"shadow_names": shadow_name}
    # Send shadow get
    r = requests.get(cloud_api_url + cloud_devices_endpoint + device_guid + cloud_shadow_endpoint, headers={"Authorization":"PAT " + token}, params=data)
    if r.status_code != 200 and r.status_code != 202:
        sys.exit("status code = " + str(r.status_code))
    return json.loads(r.text)["shadows"]

# Helper function for sending device commands to the Cloud API
# This function expects a valid LiveEdge® CLOUD Personal Access Token, device GUID, 
#   desired shadow name, and properly formatted JSON of the shadow state 
#   and returns the result of the completed command
# This function will time out if it takes too long for the command to complete in LiveEdge® CLOUD
# Constructed endpoint: https://api.videoncloud.com/v1/{device_guid}/shadows/commands/
def send_shadow_set(cloud_api_url, token, device_guid, shadow_name, settings_json):
    # Get the current device state so we have the right target version
    state = send_shadow_get(token, device_guid, shadow_name)

    # Send shadow command
    data= {
        "command_type": "set",
        "commands": [
            {
                "shadow_name": shadow_name,
                "target_version": state[0]["reported"]["current_version"],
                "state": settings_json
            }
        ]
    }
    r = requests.post(cloud_api_url + cloud_devices_endpoint + device_guid + cloud_shadow_command_endpoint, headers={"Authorization":"PAT " + token}, json=data)
    if r.status_code != 200 and r.status_code != 202:
        return json.loads(r.text)
    # Pull out command GUID from response
    command_guid = json.loads(r.text)["commands"][0]["command_guid"]
    # Poll shadow command GUID to get results
    retries = 0
    while True & retries < 5:
        time.sleep(1)
        result = requests.get(cloud_api_url + cloud_devices_endpoint + device_guid + cloud_shadow_command_endpoint + command_guid, headers={"Authorization":"PAT " + token})
        if json.loads(result.text)["command"]["finished"] == True:
            break
        retries = retries + 1
    return json.loads(result.text)

# SYSTEM
# NOTE: In the LiveEdge® CLOUD REST API, XML settings are included in the System config
def get_system_properties(token, device_guid):
    result = send_shadow_get(token, device_guid, system_shadow)
    return result[0]["reported"]["state"]


def put_system_properties(token, device_guid, target_version, json_data):
    result = send_shadow_set(token, device_guid, system_shadow, target_version, json_data)
    return result


# INPUTS

def get_in_channel_config(token, device_guid):
    result = send_shadow_get(token, device_guid, inputs_shadow)
    return result["reported"]["state"]


def put_in_channel_config(token, device_guid, json_data):
    result = send_shadow_set(token, device_guid, inputs_shadow, json_data)
    return result


# ENCODERS
#   NOTE: In the LiveEdge® CLOUD REST API, encoders are all lumped into one endpoint and intermingle
#       this means that we can simplify our setting of configurations to be a larger-batch process.
#       Editing/parsing of the JSON will have to be done at the application level and sent as a whole when saved in this app.

def get_encoders(token, device_guid):
    result = send_shadow_get(token, device_guid, encoders_shadow)
    return result["reported"]["state"]

def put_encoders_config(token, device_guid, json_data):
    result = send_shadow_set(token, device_guid, encoders_shadow, json_data)
    return result

# OUTSTREAMS
def get_out_streams(token, device_guid):
    result = send_shadow_get(token, device_guid, outputs_shadow)
    return result["reported"]["state"]

def put_out_streams(token, device_guid , json_data):
    result = send_shadow_set(token, device_guid, outputs_shadow, json_data)
    return result

# COMMANDS
def send_device_command_simple(cloud_api_url, token, device_guid, command):
    data = {
        "command": command
    }
    return requests.post(cloud_api_url + "/devices/" + device_guid + "/commands/", headers={"Authorization":"PAT " + token}, json=data)

def get_device_command_result(cloud_api_url, token, device_guid, command_guid):
    return requests.get(cloud_api_url + "/devices/" + device_guid + "/commands/" + command_guid, headers={"Authorization":"PAT " + token})

#rest_direct
def rest_direct_get(cloud_api_url, token, device_guid, rest_endpoint):
    data = {
        "command": "rest_direct_get", 
        "rest_endpoint": rest_endpoint
    }
    return requests.post(cloud_api_url + "/devices/" + device_guid + "/commands", headers={"Authorization":"PAT " + token}, json=data)

def rest_direct_post(cloud_api_url, token, device_guid, rest_endpoint):
    data = {
        "command": "rest_direct_post", 
        "rest_endpoint": rest_endpoint
    }
    return requests.post(cloud_api_url + "/devices/" + device_guid + "/commands", headers={"Authorization":"PAT " + token}, json=data)

def rest_direct_delete(cloud_api_url, token, device_guid, rest_endpoint):
    data = {
        "command": "rest_direct_delete", 
        "rest_endpoint": rest_endpoint
    }
    return requests.post(cloud_api_url + "/devices/" + device_guid + "/commands", headers={"Authorization":"PAT " + token}, json=data)

# DOCKER
def get_docker_images(cloud_api_url, token, device_guid):
    return requests.get(cloud_api_url + "/devices/" + device_guid + "/docker/images", headers={"Authorization":"PAT " + token})

def get_docker_image(cloud_api_url, token, device_guid, image_guid):
    return requests.get(cloud_api_url + "/devices/" + device_guid + "/docker/images/" + image_guid, headers={"Authorization":"PAT " + token})

def pull_docker_image(cloud_api_url, token, device_guid, repository, tag, username, password):
    data = {
        "repository": repository,
        "tag": tag,
        "username": username,
        "password": password
    }
    return requests.post(cloud_api_url + "/devices/" + device_guid + "/docker/images/", headers={"Authorization":"PAT " + token}, json=data)

def get_docker_containers(cloud_api_url, token, device_guid):
    return requests.get(cloud_api_url + "/devices/" + device_guid + "/docker/containers", headers={"Authorization":"PAT " + token})

def get_docker_container(cloud_api_url, token, device_guid, container_id):
    return requests.get(cloud_api_url + "/devices/" + device_guid + "/docker/containers/" + container_id, headers={"Authorization":"PAT " + token})

def create_docker_container(cloud_api_url, token, device_guid, container_name, image_id, restart_policy, environment_variables, volumes, ports):
    data = {
        "name": container_name,
        "image_id": image_id,
        "restart_policy": restart_policy,
        "environment": environment_variables,
        "volumes": volumes,
        "ports": ports
    }
    return requests.post(cloud_api_url + "/devices/" + device_guid + "/docker/containers/", headers={"Authorization":"PAT " + token}, json=data)

def action_docker_container(cloud_api_url, token, device_guid, container_id, action):
    data = {
        "action": action
    }
    return requests.put(cloud_api_url + "/devices/" + device_guid + "/docker/containers/" + container_id, headers={"Authorization":"PAT " + token}, json=data)

def delete_docker_container(cloud_api_url, token, device_guid, container_id, reason):
    data = {
        "reason": reason
    }
    return requests.delete(cloud_api_url + "/devices/" + device_guid + "/docker/containers/" + container_id, headers={"Authorization":"PAT " + token}, json=data)