from __future__ import division
import math
import matplotlib.pyplot as plt
import re
import glob
from PIL import Image
import tempfile


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


def output_coord_to_r_theta(coords):
  """
  Convert co-ordinates in the output image to r, theta co-ordinates.
  The r co-ordinate is scaled to range from 0 to 1.
  The theta co-ordinate is scaled to range from 0 to 1.

  A Nx2 array is returned with r being the first column and theta being the second.
  """
  # Calculate x- and y-co-ordinate offsets from the centre:
  x_offset = coords[:,0] - (output_shape[1]/2)
  y_offset = coords[:,1] - (output_shape[0]/2)

  # Calculate r and theta in pixels and radians:
  r = np.sqrt(x_offset ** 2 + y_offset ** 2)
  theta = np.arctan2(y_offset, x_offset)

  # The maximum value r can take is the diagonal corner:
  max_x_offset, max_y_offset = output_shape[1]/2, output_shape[0]/2
  max_r = np.sqrt(max_x_offset ** 2 + max_y_offset ** 2)

  # Scale r to lie between 0 and 1
  r = r / max_r

  # arctan2 returns an angle in radians between -pi and +pi. Re-scale
  # it to lie between 0 and 1
  theta = (theta + np.pi) / (2*np.pi)

  # Stack r and theta together into one array. Note that r and theta are initially
  # 1-d or "1xN" arrays and so we vertically stack them and then transpose
  # to get the desired output.
  return np.vstack((r, theta)).T


def r_theta_to_input_coords(r_theta):
  """Convert a Nx2 array of r, theta co-ordinates into the corresponding
  co-ordinates in the input image.

  Return a Nx2 array of input image co-ordinates.

  """
  # Extract r and theta from input
  r, theta = r_theta[:,0], r_theta[:,1]

  # Theta wraps at the side of the image. That is to say that theta=1.1
  # is equivalent to theta=0.1 => just extract the fractional part of
  # theta
  theta = theta - np.floor(theta)

  # Calculate the maximum x- and y-co-ordinates
  max_x, max_y = input_shape[1]-1, input_shape[0]-1

  # Calculate x co-ordinates from theta
  xs = theta * max_x

  # Calculate y co-ordinates from r noting that r=0 means maximum y
  # and r=1 means minimum y
  ys = (1-r) * max_y

  # Return the x- and y-co-ordinates stacked into a single Nx2 array
  return np.hstack((xs, ys))


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


def get_planet(coords):
  """Chain our two mapping functions together."""
  r_theta = output_coord_to_r_theta(coords)
  input_coords = r_theta_to_input_coords(r_theta)
  return input_coords
