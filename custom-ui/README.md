# Dockerized Custom UI Example

The LiveEdge Compute API gives you complete control over the functionality of your streaming device, allowing you to easily create a completely customized experience. In this example, we create a custom user interface that abstracts the complexity of setting up a new stream output by loading configuration values from an external file and presenting a simple interactive interface.

## Running the Example

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
[LiveEdge Compute Shell]: mkdir /data/local/custom-ui
```

Clone this repository to a directory on your local machine, then use `adb` to copy the files to the working directory you created on the device:

```
[Local Machine]: adb push . /data/local/custom-ui
```

Run the `docker build` command in the working directory:

```
[LiveEdge Compute Shell]: docker build -t customui-example .
```

Upon a successful build, run the container in the background to see it in action:

```
[LiveEdge Compute Shell]: docker run -p8888:8888 --name customui customui-example &
```

The container's server listens on the port provided in the `LISTENING_PORT` environment variable set in the `Dockerfile`. You can change this to whatever value makes sense for your use case. 

You should now be able to access the custom user interface by pointing your browser to `http://<device ip>:8888/`.

## The Custom UI Application - Stream-O-Matic

For this example, we created a UI intended to abstract much of the complexity of setting up streams as though we were preparing the device for sale as a consumer-grade streaming tool. The interface allows a user to select from one of the RTMP targets configured in the JSON files located in the `config/` directory. In this example, we include two such files - one for Twitch streaming and one for Twitter. 

The UI interacts with a set of RESTful API endpoints provided by the `app.py` script to react to the current state of the device and set up the streams. To try this out, connect a camera or other device to the HDMI input of your EdgeCaster, retrieve a streaming URL and stream key from the provider you'd like to try, enter it into the form fields provided, and hit the big "Ready!" button. 

## Walking Through the Code

This is a rather complex piece of example code with a number of moving parts. The core application is written in Python and uses the [Bottle](https://bottlepy.org/docs/dev/) package to handle HTTP requests and responses while relying on the [CheryPy](https://docs.cherrypy.dev/en/latest/) module to provide multi-threaded WSGI support. For the sake of simplicity, the CSS, Javascript and HTML supporting the front end can all be found in `views/customui.html` with static images hosted in the `static/images/` directory. 

The front end code relies on [jQuery](https://jquery.com/), but is otherwise standard Javascript, HTML and CSS. We avoided using one of the many popular frameworks in order to make this example accessible to developers of all skills levels, but we encourage you to adopt the framework of your choice to simplify building a custom front end. 

All of the magic really happens in the `app.py` Python script that handles the initial setup, listens for requests from the front end, and interacts with the LiveEdge Compute APIs through a set of helper functions provided in the `videon_restful.py` library. 

We have strived to document the code itself using extensive comments - what follows is a high-level overview that should be read in conjunction with the code in `app.py`.

### Setting up the Profiles
As mentioned, we configure the profiles for each of our targets using a JSON file that closely mirrors the structure of the objects accepted by the relevant API calls. Separating these configuration files is not a requirement - we did it to keep the code as clean as possible. Our script starts by loading these configurations into memory. 

The `updateProfiles()` function accesses the `/v2/encoders/vid_encoders/` and `/v2/encoders/aud_encoders/` endpoints to see which profiles are already installed in the LiveEdge Compute environment to avoid creating duplicates. If the profiles defined by our configuration files are not found, the script first creates a new video and audio profile with calls to the `videon_restful.add_vid_encoder(videon_ip)` and `videon_restful.add_aud_encoder(videon_ip)` for each one, respectively. After retrieviing the newly created ID, it follows up by sending the configuration details to each by calling the `videon_restful.put_vid_encoders_config()` and `videon_restful.put_aud_encoders_config()` functions.

### Configuring the Output Streams
Once profiles are configured on the device, you must associate them with one or more output streams. For our application, we focus exclusively on RTMP streams, but you may use the same general procedure to configure any of the streaming outputs available on your device. 

When a user selects a target and provides the URL and stream key in our user interface, our script calls the `configStream()` function, which formats the provided data and configures the selected output for the stream via the `videon_restful.put_out_streams_configs()` function. At this point, the output stream is not yet enabled - it's merely ready to go live. 

### Pushing the Output Streams Live
The "Big Red Button" on the user interface reacts to the current state of the application, only showing "Ready!" when at least one output stream is successfully configured. When pushed, that button sends a signal to the endpoint `/golive` provided by our `app.py` script. This endpoint toggles the `enable` property for each configured output stream to `true` by sending the object to the LiveEdge Compute API through the `videon_restful.put_out_streams_configs()` function. At this point, your stream should be live and viewable on the service your configured. 

### Updating the User Interface 
The UI polls the `/appstate/` endpoint served by `app.py` every few seconds, which calls the `updateState()` function to return a large object containing the entire application state.
