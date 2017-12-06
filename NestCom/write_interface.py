'''
@author: Mahendra
'''
import requests

access_tok = 'c.kmPI2RSmOSDgOzr6awWjxmDUll17q7y38MNPOWw7LoBYuqL9UNCkQ0eFfM6C3DjdPA7niMwODcAdSA5FjfkUy7t2NLGTKCgQaxO8xVUntJluUUu5nv4bH2EbKcgTYu8wtCVTd6PU2kiA1OlK'
global data

def loaddata():
    global data,access_tok
    NEST_API_URL = 'https://developer-api.nest.com/?auth={0}'
    res = requests.get(NEST_API_URL.format(access_tok))
    data = res.json()

def write_values(devtype,loc,change_prop,change_val):
    global data,access_tok
    url = 'https://developer-api.nest.com/devices/{0}/{1}?auth={2}'
    ids =[];
    for devices in data['devices'][devtype]:
        if (data['devices'][devtype][devices]['where_name']==loc):
            ids.append(data['devices'][devtype][devices]['label'])
            reqbody={}
            reqbody[change_prop]=change_val
            murl = url.format(devtype,devices,access_tok)
            res=requests.put(murl,json=reqbody)
            print(res.content)
    print(ids)

loaddata()
write_values('thermostats','Den','where_name','Office')