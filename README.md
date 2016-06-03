# skyhook-bluemix-watson

This repository includes sample code to locate Raspberry Pi device connected via Watson IoT to the cload. The position estimate is done purely based on Wi-Fi scan of nearby access points and utlizes Skyhook's Precision Location for IoT API.  The code structure is:

      a) "skyhook-device" folder - includes sample code to connect your Pi to Watson and report wifi scan
      b) "skyhook-app" folder - includes sample server application code to subscribe and receive wifi scan events from the Pi and utilize Skyhook's Precision Location for IoT API to locate the device.
      
Some more detailed steps can be found below:

1. Connect your device to Watson using: https://developer.ibm.com/recipes/tutorials/raspberry-pi-4/
2. After the device is connected and sending events to the Watson IoT client, include the following sample code in your device application to allow it to include the Wi-Fi scan in the events:

      Perform a Wi-Fi scan. If running on Linux device use the following command:
            proc = subprocess.Popen(["/sbin/wpa_cli", "scan_results"], stdout=subprocess.PIPE, universal_newlines=True)    
      Parse the scanned result and format into a JSON event including the array of APs in the following format:
          [[mac, rssi, ssid], [mac, rssi, ssid]]
          EG: [[001a1'001a1ee99745', '-47', 'tp-wpa2'], ['ee99744', '-47', 'tp-wpa']]  
          Where:
                    - mac (access point mac address identifier, 48bit string with no colons ":"
                    - rssi (signal strenght in dbm units)
                    - ssid (optional string including Wi-Fi network name)
      Send event with JSON wifi scan to Watson IoT Cloud - see the example below: 
          aps = wifi_scan();
          data={'wifiscan' : str(aps) }
          client.publishEvent("status", "json", data)
 
  The code Pi client code is included in: "skyhook-device" folder
  
3. A Location API key and URL may be obtained from Skyhook by visiting https://my.skyhookwireless.com/, creating a user account and Precision Location project. Skyhook offers temporary demonstration keys and URLs at no charge.
4. To locate your device based on the reported Wi-Fi scan events you must first configure your application to subscribe to device    
  reported events including JSON formated Wi-Fi scans. Configure your application via the following steps:

   a. Use the API key assigned by Bluemix for the device (Raspberry Pi for example) to receive and send (or subscribe). 
   b. Once your application has subscribed and received events with a JSON formated Wi-Fi scan from your device, use the Skyhook Precision Location API to position the device. The API is based on the Python function available at: "skyhook-app" folder.
   c. To integrate the function in your application, it is necessery first to initialize it by providing the Skyhook API Key and URL  obtained in the previous step. Example:

          skyhook_sdk_key = '1234567893858358385skjfhsdhjfsdfkjfhsdkwu238389839834738758sZdRL' # example key obtained from Skyhook
          skyhook_url = 'https://tfdemo-lg.trueposition.com:8443/wps2/location' # example url obtained from Skyhook
          # instantiate Skyhook class
          skyhook = Skyhook(skyhook_sdk_key, skyhook_url)
  
    When the event with a Wi-Fi scan is available use the "skyhook.getlocation()" API as shown below to locate the device:

       def event_callback(event):
           try:
              print("%-33s%-32s%s: %s" % (event.timestamp.isoformat(), event.device, event.event, json.dumps(event.data)))
              device_type, device_id = event.device.split(':')
              if 'wifiscan' in event.data:
                 aps = eval(event.data['wifiscan'])
                 if len(aps) == 0:
                    return
                 fix = skyhookx.get_location(device_id, aps)
                 if fix is None:
                    return
              print(str(fix))
      
           except Exception, ex:
           print 'exception in event_callback:', ex
The skyhook.getlocation() includes two parameters:
    device_id: id of the device. This can be the device mac address or Watson allocated ID or any other unqiue ID.
    aps: array of wifi access-points in the following format: [[mac, rssi, ssid], [mac, rssi, ssid]] 
    example: [['001a1ee99745', '-47', 'tp-wpa2'], ['001a1ee99744', '-47', 'tp-wpa']]

The function returns device location fix in the following format: {'latitude': 40.064514, 'longitude': -75.46025, 'accuracy': 13}
