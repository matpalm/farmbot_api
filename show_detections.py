#!/usr/bin/env python3

import image_db
from PIL import Image, ImageDraw, ImageColor, ImageFont
import util as u
import numpy as np

def rectangle(canvas, xy, outline, width=5):
  x0, y0, x1, y1 = xy
  corners = (x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)
  canvas.line(corners, fill=outline, width=width)

class AnnotateImageWithDetections(object):

  def __init__(self, entities_blacklist=[]):
    self.image_db = image_db.ImageDB()
    self.colours = sorted(list(ImageColor.colormap.values()))
    self.c_idx = 0
    self.entity_to_colour_map = {}
    self.entities_blacklist = set(entities_blacklist)

  def entity_to_colour(self, entity):
    if entity in self.entity_to_colour_map:
      return self.entity_to_colour_map[entity]
    c = ImageColor.getrgb(self.colours[self.c_idx])
    self.entity_to_colour_map[entity] = c
    self.c_idx += 1
    return c

  def annotate_img(self, img_full_filename, min_score=0, show_all=False):
    img = Image.open(img_full_filename)

    detections = self.image_db.detections_for_img(img_full_filename)
    if len(detections) == 0:
      print("NOTE! no detections for %s" % img_full_filename)
      return img

    # collect all detections
    bounding_boxes = []
    entities = []
    scores = []
    for entity, score, x0, y0, x1, y1 in detections:
      if entity in self.entities_blacklist:
        continue
      bounding_boxes.append([x0, y0, x1, y1])
      entities.append(entity)
      scores.append(score)
    bounding_boxes = np.stack(bounding_boxes)
    entities = np.array(entities)
    scores = np.array(scores)
    print("bounding_boxes", bounding_boxes)
    print("entities", entities)
    print("scores", scores)

    if show_all:
      picks = range(len(bounding_boxes))
    else:
      # do non max suppression to collect key bounding boxes along with
      # their corresponding suppressions
      pick_to_suppressions = u.non_max_suppression(bounding_boxes, scores=scores, overlap_thresh=0.6)
      print("pick_to_suppressions", pick_to_suppressions)
      picks = pick_to_suppressions.keys()

    # draw detections on image and show
    canvas = ImageDraw.Draw(img, 'RGBA')
    font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 20)
    for i, pick in enumerate(picks):
      score = scores[pick]
      if score < min_score:
        continue

      bounding_box = bounding_boxes[pick]
      entity = entities[pick]

      x0, y0, x1, y1 = bounding_box
      area = (x1-x0)*(y1-y0)
      alpha = 255 #int(score*200)+55)  # use score to imply alpha value; [0.0, 1.0] -> [50, 255]

      rectangle(canvas, xy=(x0, y0, x1, y1),
                outline=(*self.entity_to_colour(entity), alpha))

      if show_all:
        debug_text = "e:%s: s:%0.3f a:%0.1f  p:%d" % (entity, score, area, pick)
      else:
        suppressions = pick_to_suppressions[pick]
        debug_text = "e:%s: s:%0.3f a:%0.1f  p:%d sup:%s" % (entity, score, area, pick, suppressions)

      canvas.text(xy=(0, 25*i), text=debug_text, font=font, fill='black')
      canvas.text(xy=(1, 25*i+1), text=debug_text, font=font, fill=self.entity_to_colour(entity))
      print(debug_text)

    return img


if __name__ == "__main__":
  import argparse, sys
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--entity-blacklist', type=str, default='', help='comma seperated list of entities to ignore')
  parser.add_argument('--min-score', type=float, default=0, help='minimum detection score to show')
  parser.add_argument('--show-all', action='store_true', help='show all detections (as opposed to nonmax suppressed)')
  parser.add_argument('filename', nargs=1, help="file to show detections for")
  opts = parser.parse_args()
  print("opts %s" % opts, file=sys.stderr)

  annotator = AnnotateImageWithDetections(entities_blacklist=opts.entity_blacklist.split(","))

  img = annotator.annotate_img(opts.filename[0],
                               min_score=opts.min_score,
                               show_all=opts.show_all)
  img.show()
