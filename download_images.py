#!/usr/bin/env python

import os
import requests
import json
import creds

# keep fetching all images until there are none with an attachment of "placeholder". this
# can occur if we call this too quickly after getting an ack for a photo
retry = True
while retry:
  retry = False  # assume ok unless we see a placeholder
  headers = {'Authorization': 'Bearer ' + creds.token, 'content-type': "application/json"}
  response = requests.get('https://my.farmbot.io/api/images', headers=headers)
  images = response.json()
  for image in images:
    if 'placehold.it' in image['attachment_url']:
      # at least 1 image hasn't been uploaded properly yet;
      # sleep & retry
      time.sleep(0.1)
      retry = True
      break

for image in images:
  captured_img_name = image['meta']['name']
  if captured_img_name.startswith("/tmp/images"):
    img_name = "imgs/" + captured_img_name.replace("/tmp/images/", "") + ".jpg"
    if os.path.isfile(img_name):
      print(img_name, "*")
    else:
      print(img_name, image['attachment_url'])
      req = requests.get(image['attachment_url'], allow_redirects=True)
      open(img_name, 'wb').write(req.content)
