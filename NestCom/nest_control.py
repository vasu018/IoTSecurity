'''
@author: Mahendra
'''
import requests,json,sys
from nested_lookup import nested_lookup
access_tok = "c.jHEIksxJoWg3PvsOA7EWafIlb3cMhGIxw61OnysM5yl3lEnrTMFBzU2SZQNI0GrzqxfoRmzC80QRCVgTfJi62331eq8kydTDTWDhSIXzHuZLKm00jin33eNIjHHVxn9DJrgQIRV7eJMfSDEs"
data={}
orig_data={};
mappings = {}

def thermostats(prop,val):
    if (prop=='temperature_scale' and (val.casefold()!='c' or val.casefold()!='f')):
        return "temperature scale should be c or f"
    elif (prop=='target_temperature_c' and (val<9 or val>32)):
        return "target_temperature_c should be between 9C and 32C"
    elif (prop=='target_temperature_f' and (val<50 or val>90)):
        return "target_temperature_f should be between 50F and 90F"
    elif (prop=='target_temperature_f' and (val<50 or val>90)):
        return "target_temperature_f should be between 50F and 90F"
    elif (prop=='fan_timer_duration' and val not in [30,60,120,240,480,960]):
        return "fan_timer_duration should be one of 30,60,120,240,480,960"
    else:
        return True
 
def showhelp():
    print("1. help : to show menu options")
    print("2. show : to show the devices and structure")
    print("3. change : to change values of devices satisfying a condition")
    print("\tchange '<location> <devtype> <condition> <value> <prop> <changed value>'")
    print("\t<prop> and <changed value> are optional")    
    print("4. showvalues : To check actual property names etc.")
    print("\tshowvalues <devtype> ")
    print("\tdevtype is optional")
    print("devtype is thermostats,smoke_co_alarms,cameras etc")
    
def check_cam(prop,val):
    pass

def check_protect(prop,val):
    pass

def print_orig_data(devtype=None):
    if(devtype):
        print(json.dumps(orig_data['devices'][devtype], sort_keys=True,indent=4, separators=(',', ': ')))
    else:
        print(json.dumps(orig_data['devices'], sort_keys=True,indent=4, separators=(',', ': ')))
def loaddata():
    global data,orig_data,access_tok
    NEST_API_URL = 'https://developer-api.nest.com/?auth={0}'
    res = requests.get(NEST_API_URL.format(access_tok))
    orig_data = res.json()
    
    #loop to initialize mappings between struct,location key to name mappings and initialize structure
    for structures in orig_data['structures']:
        mappings[structures]={}
        mappings[structures]['name']=orig_data['structures'][structures]['name']
        for locations in orig_data['structures'][structures]['wheres']:
            mappings[structures][locations]=orig_data['structures'][structures]['wheres'][locations]['name']
        data[orig_data['structures'][structures]['name']]={};
        
    # load data in our data structure
    for dtypes in orig_data['devices']:
        for devices in orig_data['devices'][dtypes]:
            loc = mappings[orig_data['devices'][dtypes][devices]['structure_id']][orig_data['devices'][dtypes][devices]['where_id']]
            label = orig_data['devices'][dtypes][devices]['name']
            struct = mappings[orig_data['devices'][dtypes][devices]['structure_id']]['name']
            if loc in data[struct]:
                if dtypes in data[struct][loc]:
                    data[struct][loc][dtypes][label]=devices
                else:
                    data[struct][loc][dtypes]={}
                    data[struct][loc][dtypes][label]=devices                    

            else:
                data[struct][loc]={}
                data[struct][loc][dtypes]={}
                data[struct][loc][dtypes][label]=devices
                   
def showvalues():
    print(json.dumps(data, sort_keys=True,indent=4, separators=(',', ': ')))
                    
def write_values(loc,devtype,change_prop,change_val,cond_prop=None,cond_value=None):

    # Perform initial value checks
    perform_checks = eval(devtype)
    check_res=perform_checks(change_prop,change_val)
    if check_res is not True:
        print(check_res)
        sys.exit()
        
    url = 'https://developer-api.nest.com/devices/{0}/{1}?auth={2}'
    ids =[];
    loc_parts= loc.split(".")
    try:
        
        if len(loc_parts)==3:
            ids.append(data[loc_parts[0]][loc_parts[1]][devtype][loc_parts[2]])
        elif len(loc_parts)==2:
            if loc_parts[1] in data[loc_parts[0]]:
                for dev_id in data[loc_parts[0]][loc_parts[1]][devtype]:
                    ids.append(data[loc_parts[0]][loc_parts[1]][devtype][dev_id])
            else:
                matched = (nested_lookup(loc_parts[1], data[loc_parts[0]]))
                for dev_id in matched:
                    if dev_id in orig_data["devices"][devtype]:
                        ids.append(dev_id)
        elif len(loc_parts)==1:
            for d in nested_lookup(devtype, data[loc_parts[0]]):
                ids += (list(d.values()))
    except:
        print("Invalid path!!!")

    for devices in ids:
        res = ""
        if cond_prop and cond_value:
            if (orig_data['devices'][devtype][devices][cond_prop].lower()==cond_value.lower()):
                reqbody={}
                reqbody[change_prop]=change_val
                murl = url.format(devtype,devices,access_tok)
                res=requests.put(murl,json=reqbody)
        else:
            reqbody={}
            reqbody[change_prop]=change_val
            murl = url.format(devtype,devices,access_tok)
            res=requests.put(murl,json=reqbody)
        if(res):
            print(res.content)

if __name__ == '__main__':
    loaddata()
    action = sys.argv[1]
    condprop = None
    condval = None
    actiontable = { "show" : showvalues,
                   "help" : showhelp,
                   "change" : write_values,
                   "showvalues":print_orig_data
    }
    if not action in actiontable:
        print("invalid action. Exiting now!!!")
    else:
        actionfunc = actiontable[action]
        if(action == "change"):
            location  = sys.argv[2]
            devtype = sys.argv[3]
            changeprop = sys.argv[4]
            changeval = sys.argv[5]
            try:
                v = int(changeval)
                changeval = v
            except ValueError:
                pass
            if len(sys.argv) > 6:
                condprop = sys.argv[6]
                condval = sys.argv[7]
                try:
                    v= int(condval)
                    condval = v
                except ValueError:
                    pass
            actionfunc(location,devtype,changeprop,changeval,condprop,condval)
        elif action=="showvalues":
            if len(sys.argv)>2:
                devtype = sys.argv[2]
                actionfunc(devtype)
            else:
                actionfunc()
        else:
            actionfunc()


#showvalues()
#write_values('New CS',"thermostats",'target_temperature_f',150,"temperature_scale","F")