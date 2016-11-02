from __future__ import division
import math
import matplotlib.pyplot as plt
import re
import glob
from PIL import Image
import tempfile
import numpy as np
from skimage.transform import warp


"""
Methods used in the process of obtaining and transforming the image.

"""

def atoi(text):
  return int(text) if text.isdigit() else text


def natural_keys(text):
  """
  alist.sort(key=natural_keys) sorts in human order [1,10,2] becomes [1,2,10]
  """
  return [ atoi(c) for c in re.split('(\d+)', text) ]

def get_equi_ortho_image(img, ortho=False):

  # get data from image
  w,h,c = img.shape

  # flatten image
  img_flat = img.flatten()
  fov = 120

  # Create copies of the flatten image to work with them
  bcap = img_flat.copy()
  output = img_flat.copy()

  i = 0
  w,h,c = img.shape
  while(i < output.size):

    x = (i/3)%w - w/2
    y = int((i/3)/w - h/2)
    r = math.sqrt(pow(x,2)+pow(y,2))

    if (ortho):
      try:
        el = math.acos(r / ( h / 2))
      except:
        el = 0
    else:
      el = math.pi/2 * (1 - r / (h / 2))

    theta = math.atan2(y, x)

    f = (w/2) / math.tan( fov / 2 * math.pi / 180 )

    r2 = f * math.tan( math.pi / 2 - el)
    x2 = math.floor(r2 * math.cos(theta) + w/2)
    y2 = math.floor(r2 * math.sin(theta) + h/2)

    i2 = (int)(3 * (x2 + y2 * w))

    if (ortho):
      evalu = (r > (h/2)) or (el < (math.pi - fov/180 * math.pi)/2)
    else:
      evalu = ((r2 < 0) or (r2 >= (w/2)))


    if (evalu):
      output[i] = 0
      i+=1
      output[i] = 0
      i+=1
      output[i] = 0
      i+=1
    else:
      output[i] = bcap[i2]
      i+=1
      i2+=1
      output[i] = bcap[i2]
      i+=1
      i2+=1
      output[i] = bcap[i2]
      i+=1
      i2+=1

  img2 = np.reshape(output, (w,h,3))

  name = next(tempfile._get_candidate_names())
  plt.imsave("static/"+name, img2)

  return "static/"+name+".png"


def get_raw_panorama():
  image_list = []
  # Read all images from file
  for filename in glob.glob('*.jpg'):
    image_list.append(filename.strip())
    image_list.sort(key=natural_keys)

  images = map(Image.open, image_list)
  widths, heights = zip(*(i.size for i in images))

  total_w = sum(widths[0:7])
  total_h = sum(heights[0:3])

  new_im = Image.new('RGB', (total_w, total_h))

  x_off = 0
  y_off = 0
  for im in images:
    new_im.paste(im, (x_off, y_off))
    y_off += im.size[0]
    if y_off == 3*im.size[0]:
      y_off = 0
      x_off += im.size[0]

  name = next(tempfile._get_candidate_names())
  w,h = new_im.size
  new_im.crop((0,0, 2.15*h, h)).save("static/"+name+".png")

  return "static/"+name+".png"



