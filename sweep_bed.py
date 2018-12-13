#!/usr/bin/env python3

# do sweep back and forth across bed, at z=0, capturing images.

import argparse
import creds
from client import FarmbotClient

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--delta', type=int, default=200, help="per step delta of x, y")
parser.add_argument('--offset', type=int, default=0, help="offset to add to each x, y")
parser.add_argument('--min-x', type=int, default=0, help="min x value")
parser.add_argument('--max-x', type=int, default=2500, help="max x value")
parser.add_argument('--min-y', type=int, default=0, help="min y value")
parser.add_argument('--max-y', type=int, default=1300, help="max y value")
opts = parser.parse_args()
print("opts %s" % opts)

pts = []
sweep_y_negative = False
for x in range(opts.min_x, opts.max_x, opts.delta):
  y_range = range(opts.min_y, opts.max_y, opts.delta)
  if sweep_y_negative:
    y_range = reversed(y_range)
  sweep_y_negative = not sweep_y_negative
  for y in y_range:
    pts.append((x+opts.offset, y+opts.offset))
print(len(pts), pts)

client = FarmbotClient(creds.device_id, creds.token)
for x, y in pts:
  client.move(x, y, 0)
  client.take_photo()
client.shutdown()
