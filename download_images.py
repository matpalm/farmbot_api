#!/usr/bin/env python3

from datetime import timezone
from dateutil.parser import parse
from image_db import ImageDB
import creds
import json
import os
import requests
import sys
import time

# note: download only returns 100 at a time!
# note: we are currently ignoreing placeholders

REQUEST_HEADERS = {'Authorization': 'Bearer ' + creds.token, 'content-type': "application/json"}

image_db = ImageDB()
image_db.create_if_required()

while True:
  response = requests.get('https://my.farmbot.io/api/images', headers=REQUEST_HEADERS)
  images = response.json()
  print("#images", len(images))
  if len(images) == 0:
    exit()

  at_least_one_dup = False
  for image_info in images:

    if image_db.has_record_for_farmbot_id(image_info['id']):
      print("IGNORE! dup", image_info['id'])
      requests.delete("https://my.farmbot.io/api/images/%d" % image_info['id'],
                      headers=REQUEST_HEADERS)
      at_least_one_dup = True
      continue

    if 'placehold.it' in image_info['attachment_url']:
      print("IGNORE! placeholder", image_info['id'])
      continue

    # convert date time of capture from UTC To AEDT and extract
    # a simple string version for local image filename
    dts = parse(image_info['attachment_processed_at'])
    dts = dts.replace(tzinfo=timezone.utc).astimezone(tz=None)
    local_img_dir = "imgs/%s" % dts.strftime("%Y%m%d")
    if not os.path.exists(local_img_dir):
      os.makedirs(local_img_dir)
    local_img_name = "%s/%s.jpg" % (local_img_dir, dts.strftime("%H%M%S"))
    print(">", local_img_name)

    # download image from google storage and save locally
    captured_img_name = image_info['meta']['name']
    if captured_img_name.startswith("/tmp/images"):
      req = requests.get(image_info['attachment_url'], allow_redirects=True)
      open(local_img_name, 'wb').write(req.content)

    # add entry to db
    image_db.insert(image_info, dts, local_img_name)

    # post delete from cloud storage
    requests.delete("https://my.farmbot.io/api/images/%d" % image_info['id'],
                    headers=REQUEST_HEADERS)

  if at_least_one_dup:
    print("only at least one dup; give DELETEs a chance to work")
    time.sleep(2)
