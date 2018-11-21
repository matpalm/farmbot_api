#!/usr/bin/env python3

import creds
from client import FarmbotClient

pts = []
sweep_y_negative = False
for x in range(100, 2500, 200):
  y_range = range(0, 1200, 200)
  if sweep_y_negative:
    y_range = reversed(y_range)
  sweep_y_negative = not sweep_y_negative
  for y in y_range:
    pts.append((x, y))
print(pts)

client = FarmbotClient(creds.device_id, creds.token)
for x, y in pts:
  client.move(x, y, 0)
  client.take_photo()
client.shutdown()
