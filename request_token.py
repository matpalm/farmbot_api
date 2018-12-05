#!/usr/bin/env python3

# request a token (for creds.py)

import argparse
import json
from urllib import request

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--email', type=str, help="user email for token request")
parser.add_argument('--password', type=str, help="user password for token request")
opts = parser.parse_args()
print("opts %s" % opts)

auth_info = {'user': {'email': opts.email, 'password': opts.password }}

req = request.Request('https://my.farmbot.io/api/tokens')
req.add_header('Content-Type', 'application/json')
response = request.urlopen(req, data=json.dumps(auth_info).encode('utf-8'))

token_info = json.loads(response.read().decode())

print("mqtt host [%s]" % token_info['token']['unencoded']['mqtt'])

print("rewriting creds.py")
with open("creds.py", "w") as f:
  f.write("device_id=\"%s\"\n" % token_info['token']['unencoded']['bot'])
  f.write("token=\"%s\"\n" % token_info['token']['encoded'])
