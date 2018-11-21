#!/usr/bin/env python

import os
import requests
import json
import creds
from image_db import ImageDB
from dateutil.parser import parse
from datetime import timezone

REQUEST_HEADERS = {'Authorization': 'Bearer ' + creds.token, 'content-type': "application/json"}

# keep fetching all images until there are none with an attachment of "placeholder". this
# can occur if we call this too quickly after getting an ack for a photo
retry = True
while retry:
  retry = False  # assume ok unless we see a placeholder
  response = requests.get('https://my.farmbot.io/api/images', headers=REQUEST_HEADERS)
  images = response.json()
  for image in images:
    if 'placehold.it' in image['attachment_url']:
      # at least 1 image hasn't been uploaded properly yet;
      # sleep & retry
      time.sleep(0.1)
      retry = True
      break

image_db = ImageDB()
image_db.create_if_required()

for image_info in images:
  print(image_info)

  # convert date time of capture from UTC To AEDT and extract
  # a simple string version for local image filename
  dts = parse(image_info['attachment_processed_at'])
  dts = dts.replace(tzinfo=timezone.utc).astimezone(tz=None)
  local_img_name = "imgs/%s.jpg" % dts.strftime("%Y%m%d_%H%M%S")

  # download image from google storage and save locally
  captured_img_name = image_info['meta']['name']
  if captured_img_name.startswith("/tmp/images"):
    req = requests.get(image_info['attachment_url'], allow_redirects=True)
    open(local_img_name, 'wb').write(req.content)

  # add entry to db
  image_db.insert(image_info, dts, local_img_name)

  # post delete from cloud storage
  response = requests.delete("https://my.farmbot.io/api/images/%d" % image_info['id'],
                             headers=REQUEST_HEADERS)
