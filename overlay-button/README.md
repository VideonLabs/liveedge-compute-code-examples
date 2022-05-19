# Toggle the Graphic Overlay With a Physical Button

This example is designed to listen to presses made to a physical button (basically, anything resembling a USB Keyboard) and toggle the graphic
overlay on a running stream. This requires you to connect a device capable of generating keypress events to
the USB port on your EdgeCaster device. Anything that can generate a keypress event over USB - from a [custom Arduino project](https://www.arduino.cc/reference/en/language/functions/usb/keyboard/) to a bog standard USB keyboard - should work for this example. 


The button we used to create and test this example can be [found on Amazon](https://www.amazon.com/gp/product/B08P1GY3GN/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1)

To run this example, you will first need to connect your device to the USB port of your EdgeCaster and discover which event ID and path the system has assigned to it. **NOTE:** These values may change between device resets. 

## Find the path To Your Connected Device on the EdgeCaster

To find out the path and event ID of the connected device, you need to shell into LiveEdge Compute and source the environment:

```
[Local Machine]: adb connect <device_ip>
[Local Machine]: adb root
[Local Machine]: adb shell

[LiveEdge Compute]: source /data/local/vstream/etc/env.sh
```
Devices connected to a Linux operating system are listed under `/proc`. To see a list of all connected input devices, run:

```
[LiveEdge Compute]: cat /proc/bus/input/devices
```

This will return a rather long list of devices with details for each of them. This is a sample of the output of this command on the unit we tested this on:

```
I: Bus=0019 Vendor=0001 Product=0001 Version=0100
N: Name="gpio-keys"
P: Phys=gpio-keys/input0
S: Sysfs=/devices/soc/soc:gpio_keys/input/input4
U: Uniq=
H: Handlers=event4 cpufreq 
B: PROP=0
B: EV=3
B: KEY=8000000000000 0

I: Bus=0003 Vendor=8089 Product=0003 Version=0110
N: Name="BlackC Sayobot.cn SayoDevice M3K RGB"
P: Phys=usb-xhci-hcd.0.auto-1/input0
S: Sysfs=/devices/soc/6a00000.ssusb/6a00000.dwc3/xhci-hcd.0.auto/usb1/1-1/1-1:1.0/0003:8089:0003.0001/input/input5
U: Uniq=00B96CE6E19E
H: Handlers=kgsl mouse2 event5 cpufreq 
B: PROP=0
B: EV=12001f
B: KEY=3f0003007f 0 0 483ffff17aff32d bf54444600000000 ff0001 130f938b17c007 ffff7bfad9415fff febeffdfffefffff fffffffffffffffe
B: REL=143
B: ABS=ffffff0100000000
B: MSC=10
B: LED=ff

I: Bus=0000 Vendor=0000 Product=0000 Version=0000
N: Name="msm8996-tasha-sbc-snd-card Headset Jack"
P: Phys=ALSA
S: Sysfs=/devices/soc/soc:sound-9335/sound/card0/input6
U: Uniq=
H: Handlers=event6 
B: PROP=0
B: EV=21
B: SW=3c0d4
```

We found our device by looking at the `Name` field for each entry and seeing if we found a suitable match. In our case, the documentation that came with our button called it a "SayoDevice", which shows up clearly in the `Name` field. If you're not able to match the name, the `Phys` field should indicate it's a USB device. For example, the `Phys` field for our button is `usb-xhci-hcd.0.auto-1/input0`, indicating it's a physical device connected to the USB port. 

Look under the `Handlers` field for an event name. For our example, you can see that our button can throw a number of event types. We want the raw event data for this example, so we want the event handler. In our example above, that would be `event5`. There should be a corresponding file handle for this device - in our case, `/dev/input/event5` - on the EdgeCaster. To confirm this is your device, listen to it on the command line while pressing the keys:

```
[LiveEdge Compute]: cat /dev/input/event5 
```

If you have the correct device, each key press should send a random-looking string of characters to your screen. When you're done, hit CTRL-C.

## Understanding the Output

These random-looking strings are actually a binary packed struct that contains the details of the keypress event:

```
struct input_event {
	struct timeval time;
	unsigned short type;
	unsigned short code;
	unsigned int value;
};
```
The possible values for "type" and "code" are derived from the "Event Types" and "Keys and Buttons" as defined in the [Linux kernel headers](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h). A good explainer of these values [may also be found here](https://www.kernel.org/doc/Documentation/input/event-codes.txt).


For keypress events, we want to listen for the value of the "type" code named `EV_KEY` (0x01) - which translates into the value "1".

For our example, we're using a three-button keyboard, which is mapped to the "1", "2", and "3" keys respectively. We only want to respond when the "1" key is pressed. Looking in the relevant kernel header, we see that `KEY_1` is actually mapped to the integer value `2`. If your button submits a different value, you can change the code to listen for it by finding the relevant entry in the kernel header and setting the variable `key_pressed` in `input.py` the appropriate value. 

The last value in the struct represents the action taken on the key - this is set to `1` when the key is pressed, and `0` when it's released. 

**Note:** We noticed during testing that our buttons send a third event of type `EV_MSC` - a "miscellaneous" event. This appears to be a synchornisation event and can be safely ignored. 

## Running the Example

Download the repository to your local machine and use `adb push` to copy it to an appropriate location in your LiveEdge Compute environment (e.g. `/data/local/samples/overlay-button`). Use `adb shell` to access your LiveEdge Compute Environment shell, source the enviornment, `cd` into the directory where you copied the source files, then build the Docker container:

```
[LiveEdge Compute]: docker build -t overlay-button .
```

For the Docker container to be able to access the host environment's devices, you'll need to either explicitly give the container access to the device using the Docker `--device` flag or run the container as `--privileged`. For this example, we've chosen the latter. You must also set the environment variable `DEVICE_PATH` to the path where your device is located on the EdgeCaster.

```
[LiveEdge Compute]: docker run --privileged --env DEVICE_PATH=/dev/input/event5 --name overlay-button overlay-button &
```
If everything is configured correctly, when you stream from an HDMI input to any output, you should now see the Videon logo overlayed at the bottom right of the output video when you press your button. Pressing the button again should toggle it on and off. 
