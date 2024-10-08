# Trigger SCTE insertion and Graphic Overlay with a Physical Button

This example functions to auto-detect a USB keyboard (or USB device that can signal key presses) and make REST API calls for SCTE-35 splice marker insertion on key press.

## How to Build and Run This Example

[Click here for details on running Docker containers on the LiveEdge Node.](https://support.videonlabs.com/hc/en-us/articles/4408583092115-Using-Docker-with-LiveEdge-Compute)

This code requires that a physical device emulating a USB keyboard be connected to the USB port on your LiveEdge Node device. A simple USB keyboard should work fine and **is best to connect before running the Docker container**.

Clone this repository to your local machine, use `adb` to access your LiveEdge Compute environment, create a directory under '/data/local/' to store this code, then use `adb push` to copy the files to the directory you just created.

Use `adb shell` to access the device shell, `source` the local environment, then build the container using the Dockerfile in the code:

```
docker build -t scte35 .
```

You will need to provide privileged access to the container when you run it so it may access the host environment's devices that will be auto-detected:

```
docker run -d --restart unless-stopped --name scte35 --privileged scte35
```
The mapped key presses are detailed below:
* The "1" key will make a REST API call to the host Videon device to insert a SCTE-35 splice marker with duration of 120 seconds, Pre-roll of 0.
* The "2" key will make a REST API call to the host Videon device to insert a SCTE-35 splice marker with duration of 30 seconds, Pre-roll of 0.
* The "3" key will make a REST API call to the host Videon device to send a SCTE-35 time signal start with Duration 120 seconds and Pre-roll of 200ms.
* The "4" key will make a REST API call to the host Videon device to send a SCTE-35 time signal end and Pre-roll of 200ms.
* The "5" key will cancel all active splice commands.
