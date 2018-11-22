#!/usr/bin/env python3

from image_db import ImageDB
from PIL import Image, ImageDraw
import math
import sys

image_db = ImageDB()

xyz = list(map(int, sys.argv[1:]))
if len(xyz) == 2:  # OMG, so clumsy :/
  x, y = xyz
  z = None
else:
  x, y, z = xyz

imgs = image_db.imgs_for_coords(x, y, z)
if len(imgs) == 0:
  print("no images from", xyz)
  exit()

HW = math.ceil(math.sqrt(len(imgs)))
canvas = Image.new('RGB', (645*HW, 485*HW), (50, 50, 50))
for i, (img_id, x, y, z, img) in enumerate(imgs):
  pil_img = Image.open(img)
  draw = ImageDraw.Draw(pil_img)
  draw.text((0, 0), "%s (%d, %d, %d)" % (img, x, y, z))
  paste_x_y = (645*(i%HW), 485*(i//HW))
  canvas.paste(pil_img, paste_x_y)
canvas.save("/dev/shm/foo.png")
canvas.show()
