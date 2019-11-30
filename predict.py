#!/usr/bin/env python3

from glob import glob
from io import BytesIO
import sys

import tensorflow as tf
from tensorflow.keras import models
import numpy as np
import PIL.Image

from constants import (
    TILES_DIR, NN_MODEL_PATH, FEN_CHARS, USE_GRAYSCALE, DETECT_CORNERS
)
from train import image_data
from chessboard_finder import get_chessboard_corners
from chessboard_image import get_img_arr, get_chessboard_tiles, tile_image_data

def predict_chessboard(img_path):
    print(img_path)
    img_arr = get_img_arr(img_path)
    (corners, error) = get_chessboard_corners(img_arr, detect_corners=DETECT_CORNERS)
    if corners is not None:
        print("Found corners: {}".format(corners))
    if error:
        print(error)
        exit(1)
    tiles = get_chessboard_tiles(img_arr, corners, use_grayscale=USE_GRAYSCALE)
    fen = ''
    confidence = 1
    for i in range(8):
        for j in range(8):
            buf = BytesIO()
            tile_image_data(tiles[i*8 + j]).save(buf, format='PNG')
            img_data = tf.image.decode_image(buf.getvalue(), channels=3)
            img_data = tf.image.convert_image_dtype(img_data, tf.float32)
            img_data = tf.image.resize(img_data, [32, 32])
            (fen_char, probability) = predict_tile(img_data)
            fen += fen_char
            confidence *= probability
            print((fen_char, probability))
        if i < 7:
            fen += '/'
    print(fen)
    print(confidence)

def predict_tiles(img_data_arr):
    print(model.predict(img_data_arr, verbose=1))

def predict_tile(img_data):
    probabilities = list(
        model.predict(np.array([img_data]), verbose=1, workers=2)[0]
    )
    max_probability = max(probabilities)
    i = probabilities.index(max_probability)
    return (FEN_CHARS[i], max_probability)

if __name__ == '__main__':
    print('Tensorflow {}'.format(tf.version.VERSION))
    model = models.load_model(NN_MODEL_PATH)
    # tile_img_path = glob(TILES_DIR + '/*/*.png')[0]
    # print(tile_img_path)
    # print(predict_tile(image_data(tile_img_path)))
    if len(sys.argv) > 1:
        predict_chessboard(sys.argv[1])
