from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlparse, parse_qs
import requests, hashlib,os

NEST_API_URL = 'https://developer-api.nest.com/?auth={0}'
class GetHandler(BaseHTTPRequestHandler):
    tokens={}
    def set_token(self,prod,tok):
        GetHandler.tokens[prod] = tok
    
    def fetch_devices(self,clientid,clientsec):
        url = "https://developer-api.nest.com/"
        access_tok = GetHandler.tokens[clientid + '|||' + clientsec]
#         head = {'Content-Type':'application/json','Authorization':'Bearer '+access_tok}
        res = requests.get(NEST_API_URL.format(access_tok))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(res.content)
        
        
    def fetch_token(self,state,code):
        url = 'https://api.home.nest.com/oauth2/access_token'
        if 'client_id' in GetHandler.tokens[state[0]]:
            client_id = GetHandler.tokens[state[0]]['client_id']
            client_sec = GetHandler.tokens[state[0]]['client_sec']
        del GetHandler.tokens[state[0]]
        response = requests.post(url, {
            'code':code,
            'client_id':client_id,
            'client_secret':client_sec,
            'grant_type':'authorization_code'
        })
        res = response.json()
        if 'access_token' in res:
            GetHandler.tokens[client_id + '|||' + client_sec] = res['access_token']
            print(GetHandler.tokens[client_id + '|||' + client_sec])
#             self.send_response(200)
        
    def fetch_code(self,clientid,clientsec):
#         state = ''.join(random.choice(string.ascii_letters) for x in range(16))
        state = hashlib.md5(os.urandom(32)).hexdigest()
        GetHandler.tokens[state]={}
        GetHandler.tokens[state]['client_id']=clientid
        GetHandler.tokens[state]['client_sec']=clientsec
        print(GetHandler.tokens[state])
        url = 'https://home.nest.com/login/oauth2?client_id=' + clientid + '&state='+state
        return url
        
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if(parsed_path.path.split('/')[1]=='devices'):
            clientid = parsed_path.path.split('/')[2]
            clientsec = parsed_path.path.split('/')[3]
            query = parse_qs(parsed_path.query)
            self.fetch_token(query['state'], query['code'])
            self.fetch_devices(clientid, clientsec)
            
        if(parsed_path.path.split('/')[1]=='products'):
            client_id = parsed_path.path.split('/')[2]
            client_secret = parsed_path.path.split('/')[3]
            id = client_id + '|||' + client_secret   
            if(id not in GetHandler.tokens):
                res=self.fetch_code(client_id, client_secret)
                self.send_response(301)
                self.send_header('Location', res)
                self.end_headers()
            else:
                self.fetch_devices(client_id, client_secret)
        return        

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
