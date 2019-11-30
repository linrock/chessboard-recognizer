#!/usr/bin/env python3

# Generate tile images for all chessboard images in input folder
# Used for building training datasets

import os
from glob import glob
import argparse
import math

import numpy as np
import PIL.Image

from constants import CHESSBOARDS_DIR, TILES_DIR
from chessboard_finder import get_chessboard_corners
from chessboard_image import get_img_arr, get_chessboard_tiles_color
from chessboard_image import get_chessboard_tiles_gray

# img_filename_prefix shows which piece is on which square:
# RRqpBnNr-QKPkrQPK-PpbQnNB1-nRRBpNpk-Nqprrpqp-kKKbNBPP-kQnrpkrn-BKRqbbBp

def save_tiles(tiles, img_save_dir, img_filename_prefix):
    """ Saves all 64 tiles as 32x32 PNG files with this naming convention:

        a1_R.png (white rook on a1)
        d8_q.png (black queen on d8)
        c4_1.png (nothing on c4)
    """
    if not os.path.exists(img_save_dir):
        os.makedirs(img_save_dir)

    piece_positions = img_filename_prefix.split('-')
    files = 'abcdefgh'
    for i in range(64):
        piece = piece_positions[math.floor(i / 8)][i % 8]
        sqr_id = '{}{}'.format(files[i % 8], 8 - math.floor(i / 8))
        tile_img_filename = '{}/{}_{}.png'.format(img_save_dir, sqr_id, piece)

        # Make resized 32x32 image from matrix and save
        tile = tiles[i]
        PIL.Image.fromarray(tile, 'RGB') \
            .resize([32, 32], PIL.Image.ADAPTIVE) \
            .save(tile_img_filename)

def generate_tiles_from_all_chessboards():
    """ Generates 32x32 PNGs for each square of all chessboards
    """
    if not os.path.exists(TILES_DIR):
        os.makedirs(TILES_DIR)
    chessboard_img_filenames = glob("%s/*.png" % CHESSBOARDS_DIR)
    num_chessboards = len(chessboard_img_filenames)
    num_success = 0
    num_failed = 0
    for i, chessboard_img_path in enumerate(chessboard_img_filenames):
        print("%3d/%d %s" % (i + 1, num_chessboards, chessboard_img_path))
        img_arr = get_img_arr(chessboard_img_path)
        (corners, error) = get_chessboard_corners(img_arr, detect_corners=False)
        if corners is not None:
            print("\tFound corners: {}".format(corners))
        if error:
            print("\t{}\n".format(error))
            num_failed += 1
            continue
        tiles = get_chessboard_tiles_gray(img_arr, corners)
        if len(tiles) != 64:
            print("\t!! Expected 64 tiles. Got {}\n".format(len(tiles)))
            num_failed += 1
            continue
        img_filename_prefix = chessboard_img_path[len(CHESSBOARDS_DIR):-4]
        if img_filename_prefix[0] == '/':
            img_filename_prefix = img_filename_prefix[1:]
        img_save_dir = '{}/{}'.format(TILES_DIR, img_filename_prefix)
        print("\tSaving tiles to {}\n".format(img_save_dir))
        save_tiles(tiles, img_save_dir, img_filename_prefix)
        num_success += 1
    print(
        'Processed {} chessboard images ({} generated, {} failed)'.format(
            num_chessboards, num_success, num_failed
        )
    )

if __name__ == '__main__':
    np.set_printoptions(suppress=True, precision=2)
    generate_tiles_from_all_chessboards()
