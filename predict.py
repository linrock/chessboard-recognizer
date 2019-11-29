from glob import glob
from io import BytesIO
import sys

import tensorflow as tf
import numpy as np
import PIL.Image

from constants import TILES_DIR, NN_MODEL_PATH, FEN_CHARS
from train import image_data, create_model
from chessboard_finder import get_chessboard_corners
from chessboard_image import get_img_arr, get_chessboard_tiles_gray

def predict_chessboard(img_path):
    print(img_path)
    img_arr = get_img_arr(img_path)
    (corners, error_message) = get_chessboard_corners(img_arr)
    if corners is not None:
        print("Found corners: {}".format(corners))
    if error_message:
        print(error_message)
        exit(1)
    tiles = get_chessboard_tiles_gray(img_arr, corners)
    print(tiles.shape)
    # img_data_arr = []
    for i in range(64):
        img_data = PIL.Image.fromarray((tiles[:, :, i] * 255).astype(np.uint8))
        buf = BytesIO()
        img_data.save(buf, format='PNG')
        img_data = tf.image.decode_image(buf.getvalue(), channels=3)
        img_data = tf.image.convert_image_dtype(img_data, tf.float32)
        print(predict_tile(img_data))
        # img_data_arr.append(img_data)

def predict_tiles(img_data_arr):
    probabilities = model.predict(img_data_arr)
    print(probabilities)

def predict_tile(img_data):
    probabilities = list(model.predict(np.array([img_data]))[0])
    max_probability = max(probabilities)
    i = probabilities.index(max_probability)
    return (FEN_CHARS[i], max_probability)

if __name__ == '__main__':
    print('Tensorflow {}'.format(tf.version.VERSION))
    model = create_model()
    model.load_weights(NN_MODEL_PATH)
    tile_img_path = glob(TILES_DIR + '/*/*.png')[0]
    print(tile_img_path)
    print(predict_tile(image_data(tile_img_path)))
    if len(sys.argv) > 1:
        predict_chessboard(sys.argv[1])
