#!/usr/bin/env python
import urllib2
from lxml import etree, objectify

class Skyhook:
    """ This class can be used to get location from the Skyhook Precision Location for IoT Platform """

    # Skyhook SDK Key
    skyhook_sdk_key = None

    # Skyhook Precision Location Platform URL
    skyhook_url = None

    def __init__(self, skyhook_sdk_key, skyhook_url):
        self.skyhook_sdk_key = skyhook_sdk_key
        self.skyhook_url = skyhook_url

    def __prepare_location_rq_xml(self, device_id, aps):
        if len(aps) == 0:
            return None

        root_rq = etree.Element("LocationRQ", xmlns="http://skyhookwireless.com/wps/2005", version="2.21")
        root_rq.set("street-address-lookup", "none");
        root_rq.set("profiling", "true");

        auth_elm = etree.SubElement(root_rq, "authentication", version="2.2")
        key_elm =  etree.SubElement(auth_elm, "key")
        key_elm.set("key", self.skyhook_sdk_key);
        key_elm.set("username", device_id);

        for ap in aps:
            ap_elm =  etree.SubElement(root_rq, "access-point")
            mac =  etree.SubElement(ap_elm, "mac").text = ap[0]
            ssid =  etree.SubElement(ap_elm, "ssid").text = ap[2]
            signal =  etree.SubElement(ap_elm, "signal-strength").text = ap[1]
            age =  etree.SubElement(ap_elm, "age").text = str(0)

        return etree.tostring(root_rq);

    def __parse_location_rs_xml(self, loc_rs_xml):
        root_rs = objectify.fromstring(loc_rs_xml)
        for elm in root_rs.getiterator():
            if not hasattr(elm.tag, 'find'):
                continue
            i = elm.tag.find('}')
            if i >= 0:
                elm.tag = elm.tag[i+1:]

        objectify.deannotate(root_rs, cleanup_namespaces=True)
       
        fix = {}
        for elm in root_rs.iter():
            if elm.tag == 'latitude':
                fix['latitude'] = float(elm.text)
            elif elm.tag == 'longitude':
                fix['longitude'] = float(elm.text)
            elif elm.tag == 'hpe':
                fix['accuracy'] = int(elm.text)

        if len(fix) < 3:
            return None

        return fix

    def get_location(self, device_id, aps):
        """ Get location of 'device_id' using list of wifi access-points.
            device_id: id of the watson iot device
            aps: arrya of wifi access-points in the following format:
               [[mac, rssi, ssid], [mac, rssi, ssid]]
               [['001a1ee99745', '-47', 'tp-wpa2'], ['001a1ee99744', '-47', 'tp-wpa']] 

            returns fix, format: {'latitude': 40.064514, 'longitude': -75.46025, 'accuracy': 136}
        """

        try:

            if len(aps) == 0:
                return None
        
            loc_rq = self.__prepare_location_rq_xml(device_id, aps)
            if loc_rq is None:
                return None
        
            req = urllib2.Request(self.skyhook_url)
            req.add_header('Content-Type', 'text/xml')
            resp = urllib2.urlopen(req, loc_rq)
        
            loc_rs_xml = resp.read()
        
            fix = self.__parse_location_rs_xml(loc_rs_xml)
            return fix

        except Exception, ex:
            print ex
            return None

