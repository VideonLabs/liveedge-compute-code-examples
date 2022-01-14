# Sync Recorded Video With AWS S3 (And Other Cloud Storage Providers)

In addition to streaming live video, devices empowered by LiveEdge Compute can record video and store it on the deive for later retrieval. This also allows you to leverage LiveEdge Compute capabilities to automatically sync that recorded video with any cloud storage provider you choose. 

This Docker image uses `rclone` to easily sync your local device storage with a number of cloud providers. To use it, you must have LiveEdge Compute enabled on your device and have [set up access to it via adb](https://support.videonlabs.com/hc/en-us/articles/4403731257491-Getting-Started-with-the-LiveEdge-Compute-Toolkit). You should also have a basic understanding of [how Docker works with LiveEdge Compute](https://support.videonlabs.com/hc/en-us/articles/4408583092115-Using-Docker-with-LiveEdge-Compute).

The `monitor.sh` script uses the `inotify-tools` package to monitor changes to the directory where LiveEdge Compute stores recorded video. Currently, the script only syncs when it detects a file has been closed - when the recording has ended. This is to avoid uploading partial MP4 files, which can result in unplayable media. If your needs differ, you can easily edit the `monitor.sh` file to trigger the sync as needed. 

Edit the Dockerfile and replace the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with the appropriate values from your AWS account. You must also replace the `SYNC_BUCKET` value with the path to where you want your files stored in S3. **Note:** this is not exactly the same as the S3 URI - if the URI is `s3://videos/backup`, this value should be `videos/backup`.

Log in to the LiveEdge Compute environment using `adb shell` and set up the environment:

```
source /data/local/vstream/etc/env.sh
```

Use `mkdir` to create a directory on your device - e.g. `/data/local/aws-sync/` - then use `adb` to copy these files from your local machine to that directory. 

Next, `cd` into the directory to which you pushed the files and build the container:

```
cd /data/local/aws-sync/
docker build -t rclone-aws-sync .
```

In order to sync the recorded video, we map the local volume where LiveEdge Compute stores recorded video to an internal `/app/media` folder that the script is actually monitoring.

```
docker run --restart unless-stopped --name rclone-test -v \
 /data/local/internal_storage/savedvideo/Media/:/app/media \
 rclone-monitor &
```

The `--restart unless-stopped` flag should ensure this container is restarted any time the device restarts and will continue to run in the background until stopped using `docker stop`. 

Though this example targets AWS S3 buckets, `rclone` allows you to sync with a large number of cloud storage providers with just a few small changes in the `rclone` CLI command. For more information, see [the rclone documentation](https://rclone.org/overview/) and edit the Dockerfile to set up `rclone` for your provider of choice.