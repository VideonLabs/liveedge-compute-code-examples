# Trigger SCTE insertion and Graphic Overlay with a Physical Button

This example is an extension of the [Overlay Graphic](https://github.com/VideonLabs/liveedge-compute-code-examples/tree/main/overlay-button) tutorial. In this example, we replace the Videon logo with SMPTE color bars, which may be used by some digital clip insertion services as an insertion marker rather than SCTE35. However, to cover our bases, the same code also inserts a SCTE35 code. 

## How to Build and Run This Example

[Click here for details on running Docker containers on the EdgeCaster.](https://support.videonlabs.com/hc/en-us/articles/4408583092115-Using-Docker-with-LiveEdge-Compute)

This code requires that a physical device emulating a USB keyboard be connected to the USB port on your EdgeCaster device. A simple USB keyboard should work fine. Once connected, follow the instructions on the [Overlay Graphic example](https://github.com/VideonLabs/liveedge-compute-code-examples/tree/main/overlay-button) to find the device path for your keyboard. 

Clone this repository to your local machine, use `adb` to access your LiveEdge Compute environment, create a directory under '/data/local/' to store this code, then use `adb push` to copy the files to the directory you just created.

Use `adb shell` to access the device shell, `source` the local environment, then build the container using the Dockerfile in the code:

```
docker build -t insertion-button .
```

You will need to provide privileged access to the container when you run it so it may access the host environment's devices. You will also need to provide the DEVICE_PATH environment vairable pointing to the path LiveEdge Compute assigns to your device:

```
docker run --name insertion-button -e DEVICE_PATH=/dev/input/event5 --privileged insertion-button &
```

When you press the "1" key on your keyboard (or whichever key you configured), the SMPTE color bars should be overlayed on your video for the duration noted in the code (default is 10 seconds). 
