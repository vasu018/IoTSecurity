'''
@author: Mahendra
'''
import couchdb,requests
couch = couchdb.Server()
db = couch['nest'] # existing

NEST_API_URL = 'https://developer-api.nest.com/?auth={0}'

def fetch_devices():
    access_tok = 'c.kmPI2RSmOSDgOzr6awWjxmDUll17q7y38MNPOWw7LoBYuqL9UNCkQ0eFfM6C3DjdPA7niMwODcAdSA5FjfkUy7t2NLGTKCgQaxO8xVUntJluUUu5nv4bH2EbKcgTYu8wtCVTd6PU2kiA1OlK'
    res = requests.get(NEST_API_URL.format(access_tok))
    print(db.save(res.json()))
    
fetch_devices()
    