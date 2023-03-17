import sys
import os
import requests

URL = 'https://vpnxton.def.team/api/session/start'

if __name__ == '__main__':
    file=sys.argv[1]
    print(file)
    with open(file, 'r') as reader:
        items = reader.readlines()
        wallet = items[0].strip()
        token = items[1].strip()
        response = requests.post(URL, json={"vpn_token":token, "wallet":wallet })
        if response.status_code==200 and response.json()['status']=='connected':
            sys.exit(0)
    sys.exit(-1)
