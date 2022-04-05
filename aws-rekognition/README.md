# Real-Time Object Labeling With Amazon Rekognition

[Amazon Rekognition](https://aws.amazon.com/rekognition/) is a cloud-based machine learning service that can accept either a snippet of video or a still image and respond with analysis that can be applied to a number of use cases. In this example, we run a server from LiveEdge Compute that takes the still image produced by the EdgeCaster's live preview feature and submits it to Amazon Rekognition to identify and label the objects their models find. We then present these images as an animation with the resulting labels and bounding boxes around the region they describe.

![Screenshot of Example in Action](https://github.com/VideonLabs/liveedge-compute-code-examples/blob/main/aws-rekognition/web/screenshot.png?raw=true)

## Running This Example Locally

To start, you'll need to create an account on AWS and [set it up for use with Amazon Rekognition, according to their instructions](https://docs.aws.amazon.com/rekognition/latest/dg/setting-up.html). 

Copy the contents of this repository to your local machine and update the values in the `Dockerfile` that correspond to your AWS credentials:

```
# Make sure to set these values to your AWS credentials
ENV AWS_ACCESS_KEY_ID='[YOUR AWS ACCESS KEY ID]'
ENV AWS_SECRET_ACCESS_KEY='[YOUR AWS SECRET KEY]'
ENV AWS_REGION='[YOUR PREFERRED REGION (e.g. 'us-west-1')]'
```

Use adb to connect and access the shell to your LiveEdge Compute environment:

```
[Local Machine]: adb connect <device ip>
[Local Machine]: adb root
[Local Machine]: adb shell

[LiveEdge Compute Shell]: source /data/local/vstream/etc/env.sh
```

Create a working directory in `/data/local/`:

```
[LiveEdge Compute Shell]: mkdir /data/local/rekognition
```

Copy the files from your local machine to the EdgeCaster:

```
[Local Machine]: adb push ./ /data/local/rekognition
```

Build, then run the Docker container:

```
[LiveEdge Compute Shell]: cd /data/local/rekognition
[LiveEdge Compute Shell]: docker build -t rekognition .

[... Build output ...]

[LiveEdge Compute Shell]: docker run -p5001:5001 rekognition &
```

If everything is configured correctly and your EdgeCaster is connected and streaming video, you should then be able to visit **http://<DEVICE_IP>:5001/** in the browser on your local machine and see the example in action. 

## What is Happening in the Code

The `server.js` file is a simple NodeJS Express application that grabs the most recent JPEG image from the EdgeCaster preview, then sends it using the `axios` library to Amazon's Rekognition service. It receives the results and uses them to draw labels and bounding boxes over the image using SVG and the `sharp` library. 

The application only does this when a request is made for a new image on the `/bounded/` endpoint. The rate of access is determined by changing the interval value of the `setInterval()` Javascript function near the bottom of `/web/index.html`, which the application serves when you access the root (`/`) endpoint. 

**NOTE:** As of this writing, the Amazon Rekognition free tier is limited to 5,000 images. The script in this example makes a call once every second, which means you are likely to be charged by AWS if you keep this example running longer than 5,000 images - about an hour and a half.