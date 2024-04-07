import colorgram
import colorsys
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from sklearn.cluster import KMeans


def create_sample_image(colors, width, height):
  """Creates a sample image with specified colors"""
  # Create a new image with the specified dimensions
  img = Image.new('RGB', (width, height))

  # Create a pixel map for the image
  pixels = img.load()

  # Assign colors to the image
  for y in range(height):
    for x in range(width):
      # Use modulo to cycle through the colors array
      color_index = (y * width + x) % len(colors)
      pixels[x, y] = colors[color_index]

  return img


def get_colors(nums_colors):
  colors = colorgram.extract('images/owl.jpg', nums_colors)

  print(colors)
  list_color = []
  for color in colors:
    list_color.append(color.rgb)
  print(list_color)
  return list_color


def get_representative_colors_with_kmeans(image_path, num_colors):
  # Carga la imagen
  image = Image.open(image_path)
  small_img = image.resize((100, 100))
  # Convierte la imagen en una matriz numpy
  image_np = np.array(small_img)
  # Aplana la matriz en un arreglo 1D de píxeles
  pixels = image_np.reshape((-1, 3))

  # Realiza el agrupamiento de K-Means en los píxeles de la imagen
  kmeans = KMeans(n_clusters=num_colors)
  kmeans.fit(pixels)

  # Obtiene los centros de los clusters, que representan los colores más representativos
  representative_colors = kmeans.cluster_centers_.astype(int)

  return representative_colors


def show_color_samples(colors, img_filename):
  # Crea una figura para mostrar los cuadrados de muestra de colores
  plt.figure(figsize=(len(colors), 1))

  # Itera sobre los colores y dibuja un cuadrado de muestra para cada uno
  for i, color in enumerate(colors):
    plt.subplot(1, len(colors), i + 1)
    plt.imshow([[increase_contrast(color, 2)]])
    plt.axis('off')

  # Muestra los cuadrados de muestra de colores
  plt.savefig(img_filename, format='jpg', bbox_inches='tight', pad_inches=0)


def increase_contrast(color, factor):
  """Aumenta el contraste de un color si es vívido."""
  if is_vivid_color(color):
    r, g, b = color
    new_r = min(255, int(r * factor))
    new_g = min(255, int(g * factor))
    new_b = min(255, int(b * factor))
    return (new_r, new_g, new_b)
  else:
    return color


def get_representative_colors_with_colorgram(image_path, num_colors):
  # Extrae colores dominantes de la imagen
  colors = colorgram.extract(image_path, num_colors)

  # Convierte los colores extraídos en formato RGB
  rgb_colors = [(color.rgb.r, color.rgb.g, color.rgb.b) for color in colors]

  return rgb_colors


def is_vivid_color(color):
  """Determina si un color es vívido (saturado) basado en su saturación."""
  r, g, b = color
  h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
  return s > 0.2  # Puedes ajustar este umbral según tus necesidades


show_color_samples(
  get_representative_colors_with_kmeans('images/colibri.jpeg', 10),
  "color1.jpeg")
show_color_samples(
  get_representative_colors_with_colorgram('images/colibri.jpeg', 10),
  "color2.jpeg")

width = 200  # Width of the image
height = 200  # Height of the image
