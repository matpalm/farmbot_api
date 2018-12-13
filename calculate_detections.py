#!/usr/bin/env python3

# run faster_rcnn on all images in db that don't have detections yet.
# _highly_ recommended to set 'export TFHUB_CACHE_DIR=/data/tf_hub_module_cache/'
# note: initing the network and runs through are horrifically slow :/

import tensorflow as tf
import tensorflow_hub as hub
import sys

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

  def detections(self, img_filename):
    # run img through network
    img_bytes = open(img_filename, 'rb').read()
    detections = self.sess.run(self.detect_fn,
                               feed_dict={self.image_str: img_bytes})
    # extract fields relevant to class / score detection
    entities = detections['detection_class_entities']
    scores = detections['detection_scores']
    bbs = detections['detection_boxes']
    # flatten detections to list of tuples
    detections = []
    for entity, score, bb in zip(entities, scores, bbs):
      if score > self.min_score:
        entity = entity.decode()
        score = float(score)
        y0, x0, y1, x1 = map(float, list(bb))
        detections.append((entity, score, x0, y0, x1, y1))
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
    detections = detector.detections(filename)
    print("img_id %d  %s  #detections=%d" % (img_id, filename, len(detections)))
    image_db.insert_detections(img_id, detections)
