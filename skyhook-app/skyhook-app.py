#!/usr/bin/env python
import signal
import time
import sys
import json
import ibmiotf.application
import ibmiotf.api
from skyhook import Skyhook

skyhook_sdk_key = '1234567893858358385skjfhsdhjfsdfkjfhsdkwu238389839834738758sZdRL'
skyhook_url = 'https://tfdemo-lg.trueposition.com:8443/wps2/location'

# app credentials to connect to watson
skyhook_watson_org        = 'ABCDEF'
skyhook_watson_id         = 'truefix-watson-app'
skyhook_watson_auth_key   = '0912893298123892193'
skyhook_watson_auth_token = '3845798wkjhjskjsjs'

def event_callback(event):
    try:
        print("%-33s%-32s%s: %s" % (event.timestamp.isoformat(), event.device, event.event, json.dumps(event.data)))
        device_type, device_id =  event.device.split(':')
        if 'wifiscan' in event.data:
            aps = eval(event.data['wifiscan'])
            if len(aps) == 0:
                return
                
            fix = skyhook.get_location(device_id, aps)
            if fix is None:
                return
        
            print(str(fix))

    except Exception, ex:
        print 'exception in event_callback:', ex

def interrupt_handler(signal, frame):
    app_client.disconnect()
    sys.exit(0)


options = {
    'org'         : skyhook_watson_org,
    'id'          : skyhook_watson_id,
    'auth-key'    : skyhook_watson_auth_key,
    'auth-token'  : skyhook_watson_auth_token,
    'auth-method' : 'apikey'
}

try:
    app_client = ibmiotf.application.Client(options)
    app_client.connect()
except Exception as e:
    print(str(e))
    sys.exit()

# instantiate Skyhook class
skyhook = Skyhook(skyhook_sdk_key, skyhook_url)

# subscribe to receive events from our devices
app_client.deviceEventCallback = event_callback

while True:
    time.sleep(1)
