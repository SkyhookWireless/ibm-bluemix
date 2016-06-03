#!/usr/bin/env python
import signal
import time
import sys
import subprocess
import json
import ibmiotf.device

# device credentials to connect to watson
skyhook_watson_org         = 'abcdef'
skyhook_watson_device_type = 'tf-pi'
skyhook_watson_device_id   = 'tf-pi-1'
skyhook_watson_auth_token  = 'ABCDEFGHIJKLMNOPQR'

def wifi_scan():
    proc = subprocess.Popen(["/sbin/wpa_cli", "scan_results"], stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    aps = []
    for line in out.split("\n"):
        if ':' in line:
            lst = line.split()
            # mac, signal, ssid
            ap = [lst[0].replace(':', ''), lst[2], lst[4] if len(lst) > 4 else '']
            aps.append(ap)

    return aps


def interruptHandler(signal, frame):
    client.disconnect()
    sys.exit(0)


options = {
    'org'         : skyhook_watson_org,
    'type'        : skyhook_watson_device_type,
    'id'          : skyhook_watson_device_id,
    'auth-token'  : skyhook_watson_auth_token,
    'auth-method' : 'token'
}

try:
    client = ibmiotf.device.Client(options)
    client.connect()

    while True:
        aps = wifi_scan();
        data={'wifiscan' : str(aps) }
        client.publishEvent("status", "json", data)
        time.sleep(60)

except Exception as e:
    print(str(e))
    sys.exit()

