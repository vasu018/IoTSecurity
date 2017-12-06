'''
@author: Mahendra
'''
import requests
access_tok = 'c.FQYkAjl72lkHTiAE9JM0NjXJfOfv4JLEU2tfH1l01X7AaLJ9j8rMQJMqdoatJnrupEZHxUxAoRQxqXDvcKAzYLORsuFtHYE6Vf9qbRATkSLtEVwQxlM1M8xASDfAg52VwMsQShchGPXrakUw'
NEST_API_URL ="https://developer-api.nest.com/devices/thermostats/8TntHtD5B1kP_T9ZQ_LDcshQapVimPNC?auth={0}"
body = {}
body['label']='MP room'
murl = 'https://developer-api.nest.com/devices/thermostats/8TntHtD5B1kP_T9ZQ_LDcshQapVimPNC?auth={0}'
res = requests.put(murl.format(access_tok),json=body)
print(res.content)