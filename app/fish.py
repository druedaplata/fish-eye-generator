from __future__ import division
from flask import Flask, render_template, request
import math
import sys
import time
from scipy import misc
import matplotlib.pyplot as plt
import urllib, os
import numpy as np
import tempfile

app = Flask(__name__)
@app.route('/')
def index():
  return render_template('index.html')


@app.route('/fish', methods=['GET','POST'])
def fish():
  key = request.json['key']
  fov = request.json['fov']
  pitch = request.json['pitch']
  size = request.json['size']
  loc = request.json['loc']
  base = request.json['base']
  url = str(base + size + loc + pitch + fov + key)
  urllib.urlretrieve(url, 'static/normal.jpg')

# read temporal image
  img = plt.imread('static/normal.jpg')

  img_flat = img.flatten()

  # Create copies of the flatten image to work with them
  bcap = img_flat.copy()
  bfish = img_flat.copy()

  # Get data from original image
  width, height, c = img.shape
  fov = 120

  i = 0
  w,h,c = img.shape
  print bfish.shape
  while(i < bfish.size):

    x = (i/3)%w - w/2
    y = int((i/3)/w - h/2)
    r = math.sqrt(pow(x,2)+pow(y,2))
    el = math.pi/2 * (1 - r / (h / 2))

    theta = math.atan2(y, x)

    f = (width/2) / math.tan( fov / 2 * math.pi / 180 )

    r2 = f * math.tan( math.pi / 2 - el)
    x2 = math.floor(r2 * math.cos(theta) + w/2)
    y2 = math.floor(r2 * math.sin(theta) + h/2)

    i2 = (int)(3 * (x2 + y2 * w))

    evalu = ((r2 < 0) or (r2 >= (w/2)))
    if (evalu):
      bfish[i] = 0
      i+=1
      bfish[i] = 0
      i+=1
      bfish[i] = 0
      i+=1
    else:
      bfish[i] = bcap[i2]
      i+=1
      i2+=1
      bfish[i] = bcap[i2]
      i+=1
      i2+=1
      bfish[i] = bcap[i2]
      i+=1
      i2+=1

  img2 = np.reshape(bfish, (600,600,3))

  name = next(tempfile._get_candidate_names())

  plt.imsave("static/"+name, img2)

  return "static/"+name+".png"





if __name__ == "__main__":
    app.run()
