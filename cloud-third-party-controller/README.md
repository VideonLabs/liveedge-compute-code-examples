# Dockerized LiveEdge Cloud control UI Example
This Docker example serves as a demonstration of how a third-party controller application would interface with Videon's LiveEdge Cloud API. In this example, we step through what it takes to get a simple RTMP stream running via calls to the LiveEdge Cloud API, all from a server that can be run from anywhere (a server, your computer, or even a Videon EdgeCaster to control other Videon devices!).

This demonstration application is intended to serve as a springboard for partners to develop their own, production-ready third-party controller, not as a tool to use in a production environment. As a result, if usage instructions are followed, this example functions well to demonstrate to interact with the LiveEdge Cloud API, but may not catch all errors or handle all user error.

Documentation for LiveEdge Cloud can be found [here](https://support.videonlabs.com/hc/en-us/categories/10950511072403-LiveEdge-Cloud) and the LiveEdge Cloud API can be found [here](https://api.videoncloud.com/v1/openapi/html)

# How the app works
## videon_cloud_restful.py
This is a library that can be used as it is by partners in their controller applications. See the code comments for the suggested usage of this library.
## customui.html
This is the webpage that is hosted by the application and gathers user input to be passed to `app.py`. It primarily serves to demonstrate functionality and is, to a degree, intentionally not the most aesthetically pleasing as to discourage this example application from being used in production environments.
## app.py
This is the backend application that processes the user input from customui.html and makes the requisite calls to the `videon_cloud_restful.py` library to interact with the LiveEdge Cloud API.

# How to run the app
To run this example on your local device, you'll first need to [enroll your device in LiveEdge Cloud](https://support.videonlabs.com/hc/en-us/articles/6004577224979-How-to-use-LiveEdge-Cloud):

Clone this repository to a directory on your local machine, then:

Run the `docker build` command in the working directory:

```
docker build -t videon-cloud-example .
```

Upon a successful build, run the container in the background to see it in action:

```
docker run -p8888:8888 --name videon-cloud-connector videon-cloud-example &
```

The container's server listens on the port provided in the `LISTENING_PORT` environment variable set in the `Dockerfile`. You can change this to whatever value makes sense for your use case. 

You should now be able to access the custom user interface by pointing your browser to `http://localhost:8888/`.

# How to use the app
## Authenticating API connection with the Personal Access Token (PAT)
In order to make API calls, a Personal Access Token (PAT) is required. It is good practice to verify the PAT exists and check when it expires, in case a new PAT needs to be generated.

It is currently required for a PAT to first be created from the LiveEdge Cloud API under a [user's account settings](https://videoncloud.com/account). From that point on, a third-party controller can generate new PATs in the event that they are exposed or are about to expire.

In this app, a PAT is submitted in a plain text field and eventually passed to the `get_token_expiration()` function in `videon_cloud_restful.py` (see code comments for expected inputs and possible return values). Once a valid token is submitted, the app loads organizations that the user is a part of.

## Getting the user's organizations
In LiveEdge Cloud, devices are generally assigned to organizations, so one must specify an organization that they want to load devices from.

In this app, after the PAT is confirmed as valid, a call is made to the LiveEdge Cloud API to get the user's organizations via the `get_organizations()` function in `videon_cloud_restful.py`. Each available organization name and org_guid is loaded dynamically into the "LiveEdge Cloud Organization" dropdown in customui.html. The user then selects the organization in order to load devices that the user has access to in that organization.

## Getting devices within the user's organization
Once an organization is chosen, the PAT and respective org_guid are passed on to the `get_devices()` function in `videon_cloud_restful.py`. Device serial numbers and device_guid are loaded into the "Device" dropdown. The user then selects a device serial number from the list to load basic input status via the checklist on the webpage as well as available RTMP outputs.

## Configuring the Output Streams
For our application, we focus exclusively on RTMP streams, but one may use the same general procedure to configure any of the streaming outputs available on a device. 

When a user provides the URL and stream key in our user interface after clicking save, our script calls the `configStream()` function, which formats the provided data and configures the selected output for the stream via the `videon_cloud_restful.put_out_streams()` function. At this point, the output stream is not yet enabled - it's merely ready to go live. 

## Pushing the Output Streams Live
The "Big Red Button" on the user interface reacts to the current state of the application, only showing "Ready!" when at least one output stream is successfully configured. When pushed, that button sends a signal to the endpoint `/golive` provided by our `app.py` script. This endpoint toggles the `enable` property for each configured output stream to `true` by sending the object to the LiveEdge Compute API through the `videon_cloud_restful.put_out_streams()` function. At this point, your stream should be live and viewable on the service your configured.
