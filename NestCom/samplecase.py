'''
@author: Mahendra
'''
import smtplib,nest_control,threading,json
from sseclient import SSEClient

class myThread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        #print ("Starting " + self.name)
        listenevent(self.name)
        print ("Exiting " + self.name)

def listenevent(devid):
    NEST_API_URL = 'https://developer-api.nest.com/devices/smoke_co_alarms/{0}?auth={1}'
    events = SSEClient(NEST_API_URL.format(devid,nest_control.access_tok))
    print("listening for ",devid)
    for evt in events:
        res = json.loads(evt.data)
        if res and res['data']['co_alarm_state']!='ok':
            structname = nest_control.mappings[res['data']['structure_id']]['name']
            locname = res['data']['where_name']
#             print(structname)
            nest_control.write_values(structname+"."+locname,"thermostats",'hvac_mode','off')
            sendmail(res['data'],structname,locname)
#             for cams in nest_control.data[structname][locname]['cameras']:
#                 camid = nest_control.data[structname][locname]['cameras'][cams]
#                 print(camid)
                
        
def sendmail(dev,structname,locname):
    content =  "{0} has detected high CO Level : {1}\nLocation is {2} in {3}\nAll thermostats in this location are turned Off!!!"
    main = content.format(dev['name'],dev['co_alarm_state'],locname,structname)
#     print(main)
    msg = "\r\n".join([
  "To: mdangi@cs.stonybrook.edu",
  "Subject: Alert",
  '',
   main
  ])
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("iotlabsb@gmail.com", "Trinitron_123")
     
    server.sendmail("iotlabsb@gmail.com", "mdangi@cs.stonybrook.edu", msg)
    server.quit()

if __name__ == '__main__':
    nest_control.loaddata()
    for dev in nest_control.orig_data['devices']['smoke_co_alarms']:
        try:           
            # Create new threads
            myThread(dev).start()
        except:
            print ("Error: unable to start thread")
        
        