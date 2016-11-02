from __future__ import division
from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import urllib, os
import subprocess
from PIL import Image
import helpers


app = Flask(__name__)

input_shape = 0
output_shape = (1080, 1080)

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_patches', methods=['GET','POST'])
def get_patches():
  pano_id = request.json['pano_id']
  url = "http://cbk0.google.com/cbk?output=tile&panoid="+pano_id+"&zoom=3&x=[0-6]&y=[0-2]"
  command = "-o"
  name = "tile_#1-#2.jpg"
  cmd = ["curl", url, command, name]

  subprocess.call(cmd)

  # Get RAW panorama from multiple tiles
  img_path = helpers.get_raw_panorama()

  # Rotate image upside down
  img = Image.open(img_path)
  img.transpose(Image.FLIP_TOP_BOTTOM).save('static/mirror.png')

  img = plt.imread('static/mirror.png')
  input_shape = img.shape

  #planet_img = warp(img, get_planet, output_shape = output_shape)

  #plt.imsave('tmp.jpg', planet_img)
  return img_path


@app.route('/transform', methods=['GET','POST'])
def transform():
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

  output = {}
  output['equidistant'] = helpers.get_image(img)
  output['ortho'] = helpers.get_image(img, True)

  return jsonify(**output)


if __name__ == "__main__":
    app.run()
