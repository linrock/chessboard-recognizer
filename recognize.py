#!/usr/bin/env python3

import sys
from glob import glob
from io import BytesIO
from functools import reduce
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
from tensorflow.keras import models
import numpy as np

from constants import (
    TILES_DIR, NN_MODEL_PATH, FEN_CHARS, USE_GRAYSCALE, DETECT_CORNERS
)
from utils import compressed_fen
from train import image_data
from chessboard_finder import get_chessboard_corners
from chessboard_image import get_chessboard_tiles

def _chessboard_tiles_img_data(chessboard_img_path, options={}):
    """ Given a file path to a chessboard PNG image, returns a
        size-64 array of 32x32 tiles representing each square of a chessboard
    """
    tiles = get_chessboard_tiles(chessboard_img_path, use_grayscale=USE_GRAYSCALE)
    img_data_list = []
    for i in range(64):
        buf = BytesIO()
        tiles[i].save(buf, format='PNG')
        img_data = tf.image.decode_image(buf.getvalue(), channels=3)
        img_data = tf.image.convert_image_dtype(img_data, tf.float32)
        img_data = tf.image.resize(img_data, [32, 32])
        img_data_list.append(img_data)
    return img_data_list

def _save_output_html(chessboard_img_path, predicted_fen, confidence):
    fen = compressed_fen(predicted_fen)
    with open("debug.html", "a") as f:
        f.write('<h3>{}</h3>'.format(chessboard_img_path))
        f.write('<img src="{}" width="256" height="256"/>'.format(chessboard_img_path))
        f.write('<img src="http://www.fen-to-image.com/image/32/{}" width="256" style="margin-left: 15px"/>'.format(fen))
        f.write('<br />')
        f.write('<a href="https://lichess.org/editor/{}">{}</a>'.format(fen, fen))
        f.write('<div>{}</div>'.format(confidence))
        f.write('<br />')
        f.write('<br />')

def predict_chessboard(chessboard_img_path, options={}):
    """ Given a file path to a chessboard PNG image,
        Returns a FEN string representation of the chessboard
    """
    if not options.quiet:
        print("Predicting chessboard {}".format(chessboard_img_path))
    img_data_list = _chessboard_tiles_img_data(chessboard_img_path, options)
    predictions = []
    confidence = 1
    for i in range(64):
        # a8, b8 ... g1, h1
        tile_img_data = img_data_list[i]
        (fen_char, probability) = predict_tile(tile_img_data)
        if not options.quiet:
            print((fen_char, probability))
        predictions.append((fen_char, probability))
    predicted_fen = '/'.join(
        [''.join(r) for r in np.reshape([p[0] for p in predictions], [8, 8])]
    )
    if not options.quiet:
        confidence = reduce(lambda x,y: x*y, [p[1] for p in predictions])
        print("Confidence: {}".format(confidence))
    # if options.debug:
    print("https://lichess.org/editor/{}".format(predicted_fen))
    _save_output_html(chessboard_img_path, predicted_fen, confidence)
    print("Saved {} prediction to debug.html".format(chessboard_img_path))
    return predicted_fen

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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", help="Only print recognized FEN position",
                        action="store_true")
    parser.add_argument("-d", "--debug", help="Saves debug output to debug.html",
                        action="store_true")
    parser.add_argument("image_path", help="Path/glob to PNG chessboard image(s)")
    args = parser.parse_args()
    if not args.quiet:
        print('Tensorflow {}'.format(tf.version.VERSION))
    model = models.load_model(NN_MODEL_PATH)
    # tile_img_path = glob(TILES_DIR + '/*/*.png')[0]
    # print(tile_img_path)
    # print(predict_tile(image_data(tile_img_path)))
    if len(sys.argv) > 1:
        for chessboard_image_path in sorted(glob(args.image_path)):
            print(predict_chessboard(chessboard_image_path, args))

