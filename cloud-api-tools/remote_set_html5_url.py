import videon_cloud_restful
from urllib.parse import quote
import getopt, sys
import time

interactive = False
api_url = "https://api.videoncloud.com/v1/"
pat = ""
device_guid = ""
html5_url = ""
fps = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:d:u:f:")
except:
    print("Not enough args (-p, -d, -u, and -f required), entering interactive mode")
    interactive = True

if interactive:
    #Intro to user
    print("This Python script is intended to be used for editing the URL configured on the HTML5 container. You will need to know the Personal Access Token of an account with access to devices on which you would like perform these actions.\nThis script also assumes the HTML5 container is installed, it does not check for the container to exist.")

    # Get api url from user
    api_url = input("Enter Cloud API URL (press enter with nothing to default to production api): ")
    if api_url == "":
        print("Defaulting to production API\n")
        api_url = "https://api.videoncloud.com/v1/"

    pat_invalid = True
    while (pat_invalid):
        # Get PAT from the user
        pat = input("Enter Personal Access Token for LiveEdge Cloud: ")

        #Confirm PAT is valid, contiue if valid, ask again if invalid
        pat_check_result = videon_cloud_restful.get_token_expiration(api_url, pat)
        if pat_check_result != "Token not found":
            pat_invalid = False
        else:
            print("Invalid PAT for " + api_url + ". Please enter a valid PAT")

    # Once PAT validated, prompt for org to list devices from (list numbered options)
    org_list = videon_cloud_restful.get_organizations(api_url, pat)

    # Fill list of available org choices
    printable_org_list = ""
    for index, org in enumerate(org_list, start=1):
        printable_org_list += str(index) + ") " + org["org_name"] + "\n"

    chosen_org = input("Choose org from the list below (enter number):\n" + printable_org_list)
    org_guid = org_list[int(chosen_org) - 1]["org_guid"]

    # Once org chosen, prompt for device to install on (list numbered options)
    device_list = videon_cloud_restful.get_devices(api_url, pat, org_guid)

    printable_device_list = ""
    for index, device in enumerate(device_list, start=1):
        printable_device_list += str(index) + ") " + device["serial_number"] + "\n"

    chosen_device = input("Choose device serial number from the list below to install the HTML5 container on (enter list number):\n" + printable_device_list)
    device_guid = device_list[int(chosen_device) - 1]["device_guid"]

    action = ""
    command_guid = ""
    while action != "1" and action != "2":
        action = input("Enter the action you would like to take (enter number): \n1) Remove the HTML5 URL \n2) Set the HTML5 URL to update from\n")
    if action == "1":
        command_guid = videon_cloud_restful.rest_direct_delete(api_url, pat, device_guid, ":1323/v1/stop").json()["command_guid"]
    elif action == "2":
        html5_url = input("Enter the url: ")
        fps = input("Enter the FPS (1-4): ")
        if (int(fps) >= 1 and int(fps) <= 4):
            command_guid = videon_cloud_restful.rest_direct_post(api_url, pat, device_guid, ":1323/v1/start?url=" + quote(html5_url, safe='') + "&fps=" + fps).json()["command_guid"]
        else:
            command_guid = videon_cloud_restful.rest_direct_post(api_url, pat, device_guid, ":1323/v1/start?url=" + quote(html5_url, safe='')).json()["command_guid"]
else: # Process args and run URL command
    for o, v in opts:
        if o == "-p":
            pat = v
        elif o == "-d":
            device_guid = v
        elif o == "-u":
            html5_url = v
        elif o == "-f":
            fps = v

    print("Removing previous URL")
    command_guid = videon_cloud_restful.rest_direct_delete(api_url, pat, device_guid, ":1323/v1/stop").json()["command_guid"]
    if command_guid != "":
        command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, command_guid).json()
    while command_result["command"]["finished"] == False:
        command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, command_guid).json()
    time.sleep(3) # Need to wait 3 seconds to let the container get ready for new URL set

    command_guid = ""
    if (int(fps) >= 1 and int(fps) <= 4):
        print("Setting URL to " + html5_url + " at " + fps + " fps")
        command_guid = videon_cloud_restful.rest_direct_post(api_url, pat, device_guid, ":1323/v1/start?url=" + quote(html5_url, safe='') + "&fps=" + fps).json()["command_guid"]

if command_guid != "":
    command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, command_guid).json()
    while command_result["command"]["finished"] == False:
        command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, command_guid).json()
    print("This is the command result:\n" + str(command_result["command"]))