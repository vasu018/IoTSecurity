#!/usr/bin/python 
import subprocess
import json
import urllib2

#
# Input required to access the SmartThings Cloud
#
apiToken = "Bearer 1a5cc673-6a40-441e-84dd-422540289f1c"
apiEndpoint = "https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/db77128e-14f5-4eab-8c24-bafaca386c84"
devicePath = ""

#
# Extract devices by Location
#
def listDevicesbyLocation (location_t, deviceVendor_t):
    return 


#
# Extract devices by Device Type
#
def listDevicesbyType (deviceType_t):
    deviceType = deviceType_t
    if (deviceType == "Nest"):
	    print "Nest Devices"
    elif (deviceType == "Samsung"):
	    print "Samsung Devices"
    else:
	    print "Device type Unknown"
    print deviceType

    devices_t = [] 
    devices_t = ["dev1", "dev2", "dev3"]
    return devices_t 


#
# Extract devices by Vendor Type 
#
def listDevicesbyVendor (vendortype_t):
    return


#
# Initialization for Nest Devices 
#
def initializeNest ():
    return


#
# Initialization for Samsung Devices 
#
def initializeSamsung ():
    return


#
# Extract the data from the Samsung SmartThing Cloud.
#
def extractSTCloudData (path_t):
    pathDevicelist = path_t
    pathDevicelist.strip()
    url = apiEndpoint + "/" + pathDevicelist
    req = urllib2.Request(url)
    req.add_header('Authorization', apiToken)
    res = urllib2.urlopen(req)
    return res


#
# Main
#

#initializeSamsung ()
#initializeNest ()

#
# Switching IoT devices
#
resultSwitches = extractSTCloudData ("switches")
switches = resultSwitches.read()
print "# Switches:", switches
parsedJsonSwitches = json.loads(switches)
for switch in parsedJsonSwitches:
    #print switch
    print switch['name'] + ":" + switch['value']

#
# Contact Sensor Devices
#
resultContacts = extractSTCloudData ("contacts")
contacts = resultContacts.read()
print "# Contacts:", contacts
parsedJsonContacts = json.loads(contacts)
for contact in parsedJsonContacts:
    print contact['name'] + ":" + contact['value']

#
# Motion Sensor Devices
#
# THe "motionsensors" in the quotes should be specified in the preferences section of the Smart APP
resultMotionSensors = extractSTCloudData ("motionsensors")
motionsensors = resultMotionSensors.read()
print "# Motion Sensors:", motionsensors
parsedJsonMotionSensors = json.loads(motionsensors)
for motionsensor in parsedJsonMotionSensors:
    print motionsensor['name'] + ":" + motionsensor['value']



locationId_t = "Floor2"
deviceTyep_t = "Samsung"
deviceCategory_t = "contactSensor"
#devices = listDevicesbyLocation(locationId_t, "Samsung")
#print devices
