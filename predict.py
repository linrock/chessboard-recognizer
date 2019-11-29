from glob import glob

import tensorflow as tf
import numpy as np
import PIL.Image

from constants import TILES_DIR, FEN_CHARS
from train import image_data, create_model
from chessboard_image import get_img_arr

def predict_chessboard(img_path):
    img_arr = get_img_arr(img_path)

def predict_tile(img_path):
    data = image_data(img_path)
    probabilities = list(model.predict(np.array([data]))[0])
    max_probability = max(probabilities)
    i = probabilities.index(max_probability)
    return (FEN_CHARS[i], max_probability)

if __name__ == '__main__':
    print('Tensorflow {}'.format(tf.version.VERSION))
    model = create_model()
    model.load_weights('./model.weights')
    tile_img_path = glob(TILES_DIR + '/*/*.png')[0]
    print(tile_img_path)
    print(predict_tile(tile_img_path))
