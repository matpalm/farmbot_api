#!/usr/bin/env python3

# run faster_rcnn on all images in db that don't have detections yet.
# _highly_ recommended to set 'export TFHUB_CACHE_DIR=/data/tf_hub_module_cache/'
# note: initing the network and runs through are horrifically slow :/

from PIL import Image
from collections import namedtuple
import io
import sys
import tensorflow as tf
import tensorflow_hub as hub

Detection = namedtuple('Detection', ['theta', 'entity', 'score', 'x0', 'y0', 'x1', 'y1'])

def rotated_to_original_pixel_space(d, theta):
  # for a given detection d, that was run on an image rotated by theta, return the
  # detection in pixel space of the original unrotated image
  # TODO: Detection is close to being an object :/
  if theta == 0:
    return Detection(0, d.entity, d.score, d.x0, d.y0, d.x1, d.y1)
  if theta == 90:
    return Detection(90, d.entity, d.score, 640-d.y1, d.x0, 640-d.y0, d.x1)
  elif theta == 180:
    return Detection(180, d.entity, d.score, 640-d.x1, 480-d.y1, 640-d.x0, 480-d.y0)
  elif theta == 270:
    return Detection(270, d.entity, d.score, d.y0, 480-d.x1, d.y1, 480-d.x0)
  else:
    raise Exception("unhandled theta %s" % theta)

class Detector(object):

  def __init__(self, min_score=0.1):
    self.min_score = min_score
    detector = hub.Module("https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1")
    self.image_str = tf.placeholder(tf.string)
    image = tf.image.decode_jpeg(self.image_str)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.expand_dims(image, 0)  # single element batch
    self.detect_fn = detector(image, as_dict=True)
    self.sess = tf.Session()
    self.sess.run([tf.global_variables_initializer(), tf.tables_initializer()])

  def all_rotations_detections(self, img):
    all_detections = []
    for theta in [0, 90, 180, 270]:
      rotated_img = img.rotate(angle=theta, expand=True)
      detections = self.detections(rotated_img)
      detections = [rotated_to_original_pixel_space(d, theta) for d in detections]
      all_detections += detections
    return all_detections

  def detections(self, img):
    # convert PIL image to img bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=100)
    img_bytes = img_bytes.getvalue()

    # run img through network
    detections = self.sess.run(self.detect_fn,
                               feed_dict={self.image_str: img_bytes})

    # extract fields relevant to class / score detection
    entities = detections['detection_class_entities']
    scores = detections['detection_scores']
    bbs = detections['detection_boxes']

    # flatten detections to list of tuples
    W, H = img.size
    detections = []
    for entity, score, bb in zip(entities, scores, bbs):
      if score > self.min_score:
        entity = entity.decode()
        score = float(score)
        y0, x0, y1, x1 = map(float, list(bb))                # x, y in range (0.0, 1.0)
        x0, y0, x1, y1 = map(int, (x0*W, y0*H, x1*W, y1*H))  # mapped to pixel space (ints)
        detections.append(Detection(None, entity, score, x0, y0, x1, y1))
    return detections


if __name__ == "__main__":
  import argparse
  import image_db

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--min-score', type=float, default=0.1, help="ignore detections under this score")
  opts = parser.parse_args()
  print("opts %s" % opts, file=sys.stderr)

  detector = Detector(opts.min_score)

  image_db = image_db.ImageDB()
  for img_id, filename in image_db.img_ids_without_detections():
    pil_img = Image.open(filename)
    detections = detector.all_rotations_detections(pil_img)
    print("img_id %d  %s  #detections=%d" % (img_id, filename, len(detections)))
    image_db.insert_detections(img_id, detections)
