# Cloud Command Reciever

This is a brief example of a Docker container to run on an EdgeCaster and recieve commands from LiveEdge Cloud

In order to run this example, ensure that you have a Videon device enrolled in LiveEdge Cloud. This example also makes calls to the LiveEdge Cloud API "commands" endpoint: https://api.videoncloud.com/v1/openapi/html#operation/SendDeviceCommand

Additionally, you will need to generate a Personal Access Token (PAT) in LiveEdge Cloud, under "Access Tokens": https://videoncloud.com/account

# Running the Example Docker Container

To run this example on your local device, you'll first need to [set up your development environment](https://support.videonlabs.com/hc/en-us/articles/4403731257491-Getting-Started-with-the-LiveEdge-Compute-Toolkit) and be able to access the devuice shell through `adb`:

```
[Local Machine]: adb connect <device ip>
[Local Machine]: adb root
[Local Machine]: adb shell
```

Once logged into the device's shell, you must set up the local environment with the `source` command:

```
[LiveEdge Compute Shell]: source /data/local/vstream/etc/env.sh
```

Create a working directory in `/data/local/`:

```
[LiveEdge Compute Shell]: mkdir /data/local/cloud-command-receiver
```

Clone this repository to a directory on your local machine, then use `adb` to copy the files to the working directory you created on the device:

```
[Local Machine]: adb push . /data/local/cloud-command-receiver
```

Run the `docker build` command in the working directory:

```
[LiveEdge Compute Shell]: docker build -t cloud-command-receiver .
```

Upon a successful build, run the container in the background to see it in action:

```
[LiveEdge Compute Shell]: docker run -p8882:8882 --name cloud-receiver cloud-command-receiver &
```

### Running the Example Tests

To run the tests, you will send API calls to LiveEdge Cloud, manually entering information into the bracketed ('{...}') spaces of user information.

```
curl -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/orgs

```
Copy the GUID of the org your device is enrolled in, then

```
curl -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices?org_guid={YOUR_ORG_GUID}
```

Copy the GUID of your device, then

#### Get "Messages" Stored in Docker Container

```
curl -X POST -d '{ "command": "rest_direct_get", "rest_endpoint": ":8882/cloud-command"}' -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands
```

Copy the command GUID that is returned, then

```
curl -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands/{COMMAND_GUID}
```

This should then return information from LiveEdge Cloud that contains the list of "Message" objects stored by the Docker container as the value for the "data" field:

```
"data": { 
    "messages": [
        {
            "id": 1, 
            "message": "First message"
        }
    ]
}
```

#### Post a new "Message" to Docker Container

```
curl -X POST -d '{ "command": "rest_direct_post", "rest_endpoint": ":8882/cloud-command"}' -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands
```

Copy the command GUID that is returned, then

```
curl -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands/{COMMAND_GUID}
```

This should then return information from LiveEdge Cloud that contains the list of "Message" objects stored by the Docker container as the value for the "data" field:

```
"data": { 
    "id": 2, 
    "message": "(New) Message #2"
}
```

#### Put a new "Message" to message in Docker Container

```
curl -X POST -d '{ "command": "rest_direct_put", "rest_endpoint": ":8882/cloud-command", "data": {"id":1, "message":"First EDITED message"}}' -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands
```

Copy the command GUID that is returned, then

```
curl -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands/{COMMAND_GUID}
```

This should then return information from LiveEdge Cloud that contains the list of "Message" objects stored by the Docker container as the value for the "data" field:

```
"data": {
    "id": 1,
    "message": "First EDITED message"
}
```

#### Delete a "Message" in Docker Container (Not available in this example yet)

```
curl -X POST -d '{ "command": "rest_direct_delete", "rest_endpoint": ":8882/cloud-command/1" }' -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands
```

Copy the command GUID that is returned, then

```
curl -H "Authorization: PAT {YOUR_PAT}" https://api.videoncloud.com/v1/devices/{YOUR_DEVICE_GUID}/commands/{COMMAND_GUID}
```

This should then return information from LiveEdge Cloud that contains the list of "Message" objects stored by the Docker container as the value for the "data" field:

```

```