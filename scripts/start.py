import sys
import os
import requests

URL = 'https://vpnxton.def.team/api/session/start'

if __name__ == '__main__':
    file=sys.argv[1]
    with open(file, 'r') as reader:
        items = reader.readlines()
        token = items[0]
        response = requests.post(url, json={"vpn_token":token})
        if response.status_code==200 and response.json()['status']=='connected':
            sys.exit(0)
    sys.exit(-1)
