#!/usr/bin/env python3

import sys
from glob import glob
from io import BytesIO
from functools import reduce

import tensorflow as tf
from tensorflow.keras import models
import numpy as np

from constants import (
    TILES_DIR, NN_MODEL_PATH, FEN_CHARS, USE_GRAYSCALE, DETECT_CORNERS
)
from train import image_data
from chessboard_finder import get_chessboard_corners
from chessboard_image import get_img_arr, get_chessboard_tiles

def _chessboard_tiles_img_data(chessboard_img_path):
    img_arr = get_img_arr(chessboard_img_path)
    (corners, error) = get_chessboard_corners(
        img_arr,
        detect_corners=DETECT_CORNERS
    )
    if corners is not None:
        print("Found corners: {}".format(corners))
    if error:
        print(error)
        exit(1)
    tiles = get_chessboard_tiles(img_arr, corners, use_grayscale=USE_GRAYSCALE)
    img_data_list = []
    for i in range(64):
        buf = BytesIO()
        tiles[i].save(buf, format='PNG')
        img_data = tf.image.decode_image(buf.getvalue(), channels=3)
        img_data = tf.image.convert_image_dtype(img_data, tf.float32)
        img_data = tf.image.resize(img_data, [32, 32])
        img_data_list.append(img_data)
    return img_data_list

def predict_chessboard(chessboard_img_path):
    print("Predicting chessboard")
    print(chessboard_img_path)
    img_data_list = _chessboard_tiles_img_data(chessboard_img_path)
    predictions = []
    confidence = 1
    for i in range(64):
        # a8, b8 ... g1, h1
        tile_img_data = img_data_list[i]
        (fen_char, probability) = predict_tile(tile_img_data)
        print((fen_char, probability))
        predictions.append((fen_char, probability))
    fen = '/'.join(
        [''.join(r) for r in np.reshape([p[0] for p in predictions], [8, 8])]
    )
    print(fen)
    print(reduce(lambda x,y: x*y, [p[1] for p in predictions]))

def predict_tile(tile_img_data):
    """ Given the image data of a tile, try to determine what piece
        is on the tile, or if it's blank.

        Returns a tuple of (predicted FEN char, confidence)
    """
    probabilities = list(model.predict(np.array([tile_img_data]))[0])
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
