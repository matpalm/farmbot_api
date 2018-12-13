import numpy as np

# https://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/
def non_max_suppression(boxes, scores, overlap_thresh):
  # if there are no boxes, return an empty list
  if len(boxes) == 0:
    return []

  # if the bounding boxes integers, convert them to floats --
  # this is important since we'll be doing a bunch of divisions
  if boxes.dtype.kind == "i":
    boxes = boxes.astype("float")

  # grab the coordinates of the bounding boxes
  x1 = boxes[:,0]
  y1 = boxes[:,1]
  x2 = boxes[:,2]
  y2 = boxes[:,3]

  # compute the area of the bounding boxes and sort the bounding
  # boxes by the bottom-right y-coordinate of the bounding box
  area = (x2 - x1 + 1e-10) * (y2 - y1 + 1e-10)
  idxs = np.argsort(scores)

  # { pick idxs: suppressions } to return
  pick_to_suppressions = {}

  # keep looping while some indexes still remain in the indexes list
  while len(idxs) > 0:

    # grab the last index in the indexes list and add the
    # index value to the list of picked indexes
    last = len(idxs) - 1
    i = idxs[last]

    # find the largest (x, y) coordinates for the start of
    # the bounding box and the smallest (x, y) coordinates
    # for the end of the bounding box
    xx1 = np.maximum(x1[i], x1[idxs[:last]])
    yy1 = np.maximum(y1[i], y1[idxs[:last]])
    xx2 = np.minimum(x2[i], x2[idxs[:last]])
    yy2 = np.minimum(y2[i], y2[idxs[:last]])

    # compute the width and height of the bounding box
    w = np.maximum(0, xx2 - xx1 + 1)
    h = np.maximum(0, yy2 - yy1 + 1)

    # compute the ratio of overlap
    overlap = (w * h) / area[idxs[:last]]

    # delete all indexes from the index list that have suppressed
    suppressed_idxs = np.concatenate(([last], np.where(overlap > overlap_thresh)[0]))
    pick_to_suppressions[i] = list(reversed(idxs[suppressed_idxs[1:]]))  # ignore first since it's the same as i
    idxs = np.delete(idxs, suppressed_idxs)

  # return picks
  return pick_to_suppressions
