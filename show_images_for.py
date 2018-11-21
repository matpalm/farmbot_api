#!/usr/bin/env python3

from image_db import ImageDB
from PIL import Image
import math
import sys

image_db = ImageDB()

imgs = image_db.imgs_for_x_y(int(sys.argv[1]), int(sys.argv[2]))
if len(imgs) == 0:
  exit()

HW = math.ceil(math.sqrt(len(imgs)))
canvas = Image.new('RGB', (645*HW, 485*HW), (50, 50, 50))
for i, (_, img) in enumerate(imgs):
  pil_img = Image.open(img)
  paste_x_y = (645*(i%HW), 485*(i//HW))
  canvas.paste(pil_img, paste_x_y)
canvas.show()
