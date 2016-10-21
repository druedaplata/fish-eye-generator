from __future__ import division
from flask import Flask, render_template, request
from math import *
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
  imgh, imgw, bits = img.shape
  wh = int(imgw / 2)
  hh = int(imgh / 2)

  img2 = img.copy()
  img2[0:imgh] = (0,0,0)

  def getcentre( p ): return (p[0] - wh, p[1] - hh)
  def decentre ( p ): return (int( p[0] + wh ), int( p[1] + hh ))
  def polar    ( p ): return (sqrt( p[0]**2 + p[1]**2 ), atan2( p[1], p[0] ))
  def cartesian( p ): return (p[0] * cos( p[1] ), p[0] * sin( p[1] ))
  def normalize( p ): return (radians( hfov ) * (p[0]/wh), radians( hfov ) * (p[1]/wh))
  def spaceout ( p ): return ((p[0] * wh) / radians( hfov ), (p[1] * wh) / radians( hfov ))
  fov = 180
  hfov = fov / 2
  scale      = 1.0 - ((fov - 90) / 340) ** 1.5 if fov > 90 else 1.0
  for y in range(imgh):
    for x in range(imgw):
      p = polar( normalize( getcentre( (x, y) ) ) )
      p = (tan( 2*atan( p[0]/2 ) ) * scale, p[1])
      p = decentre( spaceout( cartesian( p ) ) )
      if p[1] >= 0 and p[1] < imgh and p[0] > 0 and p[0] < imgw:
        img2[y,x] = img[p[1],p[0]]

  name = next(tempfile._get_candidate_names())

  plt.imsave("static/"+name, img2)

  return "static/"+name+".png"





if __name__ == "__main__":
    app.run()
