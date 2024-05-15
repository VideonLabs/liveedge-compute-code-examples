# Cloud API Tools

The following scripts serve as examples and starting points when using the LiveEdge Cloud API:
* videon_cloud_restful.py - Helper script that allows calling functions to make API calls, rather than having to construct them from scratch
* * This script does not contain all LiveEdge Cloud API calls, but contains many that cen be used as examples if others not in the collection are needed
* install_html5.py - A script that installs Videon's HTML5 graphic overlay rendering container
* remote_set_html5_url.py - A script that sets the URL for the HTML5 graphic overlay rendering container to pull from

## Prerequisites
* [Personal Access Token](https://support.videonlabs.com/hc/en-us/articles/26682977851795-Generating-a-Personal-Access-Token)
* [Device GUID](https://support.videonlabs.com/hc/en-us/articles/26901717270035-Finding-the-GUID-of-a-Videon-device-in-LiveEdge-Cloud-Control)


## Using install_html5.py

This script is designed to have 2 "modes": automation and interactive

"Automation" is utilized by passing in arguments (all required) to the script in the following format:

```
python3 install_html5.py -p [personal_access_token] -d [device_guid] -n [container_display_name]
```

"Interactive" is utilized by not passing any arguments and following the prompts, entering in the requested information.

## Using remote_set_html5_url.py

This script is designed to have 2 "modes": automation and interactive

"Automation" is utilized by passing in arguments (all required) to the script in the following format:

```
python3 remote_set_html5_url.py -p [personal_access_token] -d [device_guid] -u [html5_url] -f [fps]
```

* HTML5 URL must be a valid(reachable) URL, otherwise the container will enter an error state, requiring a restart.
* FPS must be a value between 1-4

"Interactive" is utilized by not passing any arguments and following the prompts, entering in the requested information.
* If using interactive mode to replace a current URL, the URL must first be removed via the script option, then the new URL may be set via that script option