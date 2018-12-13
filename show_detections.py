#!/usr/bin/env python3

import image_db
import argparse
from PIL import Image, ImageDraw, ImageColor, ImageFont
import sys
import util as u
import numpy as np

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--entity-blacklist', type=str, default='', help='comma seperated list of entities to ignore')
parser.add_argument('filename', nargs=1, help="file to show detections for")
opts = parser.parse_args()
print("opts %s" % opts, file=sys.stderr)

full_image_filename = opts.filename[0]
img = Image.open(full_image_filename)
W, H = img.size

image_db = image_db.ImageDB()
detections = image_db.detections_for_img(full_image_filename)
if len(detections) == 0:
  print("NOTE! no detections for %s" % full_image_filename)
  img.show()
  exit()

font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 20)
colours = sorted(list(ImageColor.colormap.values()))

def rectangle(canvas, xy, outline, width=5):
  x0, y0, x1, y1 = xy
  corners = (x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)
  canvas.line(corners, fill=outline, width=width)

c_idx = 0
entity_to_colour_map = {}
def entity_to_colour(entity):
  global c_idx
  global entity_to_colour_map
  if entity in entity_to_colour_map:
    return entity_to_colour_map[entity]
  c = ImageColor.getrgb(colours[c_idx])
  entity_to_colour_map[entity] = c
  c_idx += 1
  return c

# collect all detections
bounding_boxes = []
entities = []
scores = []
entities_blacklist = set(opts.entity_blacklist.split(","))
for entity, score, x0, y0, x1, y1 in detections:
  if entity in entities_blacklist:
    continue
  bounding_boxes.append([x0*W,y0*H,x1*W,y1*H])
  entities.append(entity)
  scores.append(score)
bounding_boxes = np.stack(bounding_boxes)
entities = np.array(entities)
scores = np.array(scores)
print("bounding_boxes", bounding_boxes)
print("entities", entities)
print("scores", scores)

# do non max suppression to collect key bounding boxes along with
# their corresponding suppressions
pick_to_suppressions = u.non_max_suppression(bounding_boxes, scores=scores, overlap_thresh=0.6)
print("pick_to_suppressions", pick_to_suppressions)

# draw detections on image and show
canvas = ImageDraw.Draw(img, 'RGBA')
for i, pick in enumerate(pick_to_suppressions.keys()):

  bounding_box = bounding_boxes[pick]
  entity = entities[pick]
  score = scores[pick]
  suppressions = pick_to_suppressions[pick]

  x0, y0, x1, y1 = bounding_box
  area = (x1-x0)*(y1-y0)
  alpha = 255 #int(score*200)+55)  # use score to imply alpha value; [0.0, 1.0] -> [50, 255]

  rectangle(canvas, xy=(x0, y0, x1, y1),
            outline=(*entity_to_colour(entity), alpha))

  debug_text = "e:%s: s:%0.3f a:%0.1f  p:%d sup:%s" % (entity, score, area, pick, pick_to_suppressions[pick])
  canvas.text(xy=(0, 25*i), text=debug_text, font=font, fill='black')
  canvas.text(xy=(1, 25*i+1), text=debug_text, font=font, fill=entity_to_colour(entity))
  print(debug_text)

img.show()
