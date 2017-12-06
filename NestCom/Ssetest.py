'''
Created on Nov 13, 2016

@author: Mahendra
'''
from sseclient import SSEClient

NEST_API_URL = 'https://developer-api.nest.com/devices/thermostats/*/temperature_scale?auth={0}'
access_tok = "c.jHEIksxJoWg3PvsOA7EWafIlb3cMhGIxw61OnysM5yl3lEnrTMFBzU2SZQNI0GrzqxfoRmzC80QRCVgTfJi62331eq8kydTDTWDhSIXzHuZLKm00jin33eNIjHHVxn9DJrgQIRV7eJMfSDEs"
messages = SSEClient(NEST_API_URL.format(access_tok))
for msg in messages:
    print(msg.data)
    