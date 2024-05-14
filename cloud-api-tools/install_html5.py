import videon_cloud_restful
import getopt, sys
import time

repository = "videonlabs/html5-graphics-renderer:latest"
api_url = "https://api.videoncloud.com/v1/"
pat = ""
tag = "latest"
container_name = "HTML5"
restart_policy = {"name": "always", "MaximumRetryCount": 0}
env_vars = []
volumes = [{"host_path":"/data/local/vl-html-file-overlay-app", "container_path": "/app/persist", "mode": "rw"}]
ports = [{"host_port": 1323, "container_port": 1323}]
interactive = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:d:n:")
except:
    print("Not enough args (-p, -d, and -n required), entering interactive mode")
    interactive = True

if interactive:
    #Intro to user
    print("This Python script is intended to be used for remote installation of the HTML5 Docker container sourced by Videon Labs. You will need to know the Personal Access Token of an account with access to devices on which you would like to install the HTML5 Docker container.")

    # Get api url from user
    api_url = input("Enter Cloud API URL (press enter with nothing to default to production api): ")

    if pat:
        pat_invalid = False
    else:
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

    repository = input("Enter the image repository you would like to pull (entering blank will use default HTML5 image): ")
else:
    for o, v in opts:
        if o == "-p":
            pat = v
        elif o == "-d":
            device_guid = v
        elif o == "-n":
            container_name = v

# Once device chosen, install the HTML5 container on the device
print("Pulling " + repository)
image_command_guid = videon_cloud_restful.pull_docker_image(api_url, pat, device_guid, repository, tag, "", "").json()["command_guid"]


command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, image_command_guid).json()
while command_result["command"]["finished"] == False:
    command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, image_command_guid).json()

if command_result["command"]["response"]["result"]["state"] != "COMPLETE":
    print("Pulling image failed, please try again")
else:
    print("Successfully pulled " + repository)
    if interactive:
        container_name = input("Enter the container name you would like to assign (entering blank will use \"HTML5\"): ")

    old_container_id = ""

    image_found = False
    while not image_found:
        print("Waiting for " + repository + " image to be present in Docker state...")
        time.sleep(5)
        images = videon_cloud_restful.get_docker_images(api_url, pat, device_guid).json()["images"]
        for image in images:
            if image["tags"] != []:
                if image["tags"][0] == repository:
                    image_found = True
                    current_containers = videon_cloud_restful.get_docker_containers(api_url, pat, device_guid).json()["containers"]

                    for container in current_containers:
                        if container["name"] == container_name:
                            old_container_id = container["id"]
                            kill_command_guid = videon_cloud_restful.action_docker_container(api_url, pat, device_guid, old_container_id, "kill").json()["command_guid"]
                            command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, kill_command_guid).json()
                            while command_result["command"]["finished"] == False:
                                command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, kill_command_guid).json()

                            if command_result["command"]["response"]["result"]["state"] != "COMPLETE":
                                print("Killing old " + container_name + " container failed, it may not be running, or please try again")
                            else:
                                print("Killed old " + container_name + " container")
                            delete_command_guid = videon_cloud_restful.delete_docker_container(api_url, pat, device_guid, container["id"], "Deleting duplicate").json()["command_guid"]
                            command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, delete_command_guid).json()
                            while command_result["command"]["finished"] == False:
                                command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, delete_command_guid).json()

                            if command_result["command"]["response"]["result"]["state"] != "COMPLETE":
                                print("Deleting old " + container_name + " container failed, it may not exist, or please try again")
                            else:
                                print("Deleted old " + container_name + " container.")
                            break
                    
                    print("Attempting to create the " + container_name + " container")
                    create_command_guid = videon_cloud_restful.create_docker_container(api_url, pat, device_guid, container_name, image["id"], restart_policy,  env_vars, volumes, ports).json()["command_guid"]
                    break

    command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, create_command_guid).json()
    while command_result["command"]["finished"] == False:
        command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, create_command_guid).json()

    if command_result["command"]["response"]["result"]["state"] != "COMPLETE":
        print("Creating " + container_name + " container failed, please try again")
    else:
        print("Created " + container_name + " container. Waiting for Docker state to propagate...")


        
        container_found = False
        while not container_found:
            new_containers = videon_cloud_restful.get_docker_containers(api_url, pat, device_guid).json()["containers"]
            for container in new_containers:
                if container["name"] == container_name and container["id"] != old_container_id:
                    container_found = True
                    action_command_guid = videon_cloud_restful.action_docker_container(api_url, pat, device_guid, container["id"], "start").json()["command_guid"]
                    print("Attempting to start container")
                    break
            time.sleep(5)

        command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, action_command_guid).json()
        while command_result["command"]["finished"] == False:
            command_result = videon_cloud_restful.get_device_command_result(api_url, pat, device_guid, action_command_guid).json()

        if command_result["command"]["response"]["result"]["state"] != "COMPLETE":
            print(command_result)
            print("Starting container failed, please try again")
        else:
            print(container_name + " container started! Port config is " + str(ports[0]))
