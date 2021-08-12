import requests
import json
import sys
import os

system_url = 'http://{}:2020/v2/system'
in_channels_url = 'http://{}:2020/v2/in_channels'
in_channel_config_url = 'http://{}:2020/v2/in_channels/{}'
encoders_url = 'http://{}:2020/v2/encoders'
vid_encoders_url = 'http://{}:2020/v2/encoders/vid_encoders'
vid_encoder_config_url = 'http://{}:2020/v2/encoders/vid_encoders/{}'
sync_group_url = 'http://{}:2020/v2/encoders/vid_encoders/sync_groups'
sync_group_config_url = 'http://{}:2020/v2/encoders/vid_encoders/sync_groups/{}'
aud_encoders_url = 'http://{}:2020/v2/encoders/aud_encoders'
aud_encoder_config_url = 'http://{}:2020/v2/encoders/aud_encoders/{}'
out_streams_url = 'http://{}:2020/v2/out_streams'
out_stream_config_url = 'http://{}:2020/v2/out_streams/{}'
storage_url = 'http://{}:2020/v2/storage'
storage_device_url = 'http://{}:2020/v2/storage/{}'
scte35_url = 'http://{}:2020/v2/scte35'
scte35_splice_url = 'http://{}:2020/v2/scte35/insert_splice'
xml_url = 'http://{}:2020/v2/xml'

set_password_cgi = 'http://{}/cgi-bin/set_password.cgi?password={}'
get_ftp_history_cgi = 'http://{}/cgi-bin/get_ftp_history.cgi'
check_authentication_enabled_cgi = 'http://{}/cgi-bin/check_authentication_enabled.cgi'
reset_settings_cgi = 'http://{}/cgi-bin/reset_settings.cgi'


# GETs

def get_json(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        sys.exit("status code = " + str(r.status_code))
    json_data = json.loads(r.text)
    return json_data


# SYSTEM

def get_system_properties(ip):
    url = system_url.format(ip)
    return get_json(url)


def put_system_properties(ip, json_data):
    url = system_url.format(ip)
    put_data = None
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = str(put_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret


# INPUT CHANNEL

def get_in_channels(ip):
    url = in_channels_url.format(ip)
    return get_json(url)


def get_in_channel_config(ip, in_channel_id):
    url = in_channel_config_url.format(ip, str(in_channel_id))
    return get_json(url)


def put_in_channel_config(ip, in_channel_id, json_data):
    url = in_channel_config_url.format(ip, str(in_channel_id))
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = str(put_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret


# ENCODERS

def get_encoders(ip):
    url = encoders_url.format(ip)
    return get_json(url)


# VID ENCODERS

def get_vid_encoders(ip):
    url = vid_encoders_url.format(ip)
    return get_json(url)


def add_vid_encoder(ip):
    url = vid_encoders_url.format(ip)
    r = requests.post(url)
    return r.json()


def get_vid_encoders_config(ip, vid_encoder_id):
    url = vid_encoder_config_url.format(ip, str(vid_encoder_id))
    return get_json(url)


def put_vid_encoders_config(ip, vid_encoder_id, json_data):
    url = vid_encoder_config_url.format(ip, str(vid_encoder_id))
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = {str(put_data.status_code) : put_data.text}
    else:
        ret = "Finished with unknown result"
    return ret


# AUD ENCODERS
def get_aud_encoders(ip):
    url = aud_encoders_url.format(ip)
    return get_json(url)


def add_aud_encoder(ip):
    url = aud_encoders_url.format(ip)
    r = requests.post(url)
    return r.json()


def get_aud_encoders_config(ip, aud_encoder_id):
    url = aud_encoder_config_url.format(ip, str(aud_encoder_id))
    return get_json(url)


def put_aud_encoders_config(ip, aud_encoder_id, json_data):
    url = aud_encoder_config_url.format(ip, str(aud_encoder_id))
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = str(put_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret


# SYNC GROUPS

def get_sync_groups(ip):
    url = sync_group_url.format(ip)
    return get_json(url)


def add_sync_group(ip):
    url = sync_group_url.format(ip)
    r = requests.post(url)
    return r


def get_sync_group_config(ip, sync_group_id):
    url = sync_group_config_url.format(ip, str(sync_group_id))
    return get_json(url)


def put_sync_group_config(ip, sync_group_id, json_data):
    url = sync_group_config_url.format(ip, str(sync_group_id))
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = str(put_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret


# OUTSTREAMS
def get_out_streams(ip):
    url = out_streams_url.format(ip)
    return get_json(url)


def get_out_streams_configs(ip, out_stream_id):
    url = out_stream_config_url.format(ip, str(out_stream_id))
    return get_json(url)


def put_out_streams_configs(ip, out_stream_id, json_data):
    url = out_stream_config_url.format(ip, str(out_stream_id))
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = str(put_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret


# XML
def get_xml_properties(ip):
    url = xml_url.format(ip)
    return get_json(url)


def put_xml_properties(ip, json_data):
    url = xml_url.format(ip)
    put_data = None
    try:
        put_data = requests.put(url, data=json.dumps(json_data), timeout=5)
    except requests.exceptions.Timeout:
        pass
    if put_data is not None:
        ret = str(put_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret

# STORAGE
def get_storage(ip):
    url = storage_url.format(ip)
    return get_json(url)


# CGI SCRIPTS
def set_authentication_password(ip, password):
    url = set_password_cgi.format(ip, str(password))
    try:
        get_data = requests.get(url)
    except requests.exceptions.Timeout:
        pass
    if get_data is not None:
        ret = str(get_data.status_code)
    else:
        ret = "Finished with unknown result"
    return ret

def get_ftp_history(ip, use_adb=False):
    if use_adb:
        os.system('adb shell "source /data/local/vstream/etc/env.sh && ./data/local/vstream/usr/local/www/cgi-bin/get_ftp_history.cgi" > get_ftp_history.txt')
        if os.path.exists('get_ftp_history.txt'):
            fp = open('get_ftp_history.txt', "r")
            file_data = fp.read()
            fp.close()
            return file_data
        else:
            sys.exit("Unable to get ftp history")
    else:
        url = get_ftp_history_cgi.format(ip)
        get_data = requests.get(url)
        if get_data.status_code != requests.codes.ok:
            sys.exit("status code = " + str(get_data.status_code))
        return get_data.text

def get_authentication_enabled(ip):
    url = check_authentication_enabled_cgi.format(ip)
    get_data = requests.get(url)
    if get_data.status_code != requests.codes.ok:
        sys.exit("status code = " + str(get_data.status_code))
    return get_data.text != ""


def reset_device_adb():
    os.system("adb root && adb shell 'source /data/local/vstream/etc/env.sh && ./data/local/vstream/usr/local/www/cgi-bin/reset_settings.cgi' > /dev/null")


def reset_device_ip(ip):
    url = reset_settings_cgi.format(ip)
    requests.get(url)