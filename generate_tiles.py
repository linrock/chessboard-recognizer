#!/usr/bin/env python3

# Generate tile images for all chessboard images in input folder
# Used for building training datasets

import os
from glob import glob
import argparse
import math

import numpy as np
import PIL.Image

from constants import CHESSBOARDS_DIR, TILES_DIR, USE_GRAYSCALE
from chessboard_image import get_chessboard_tiles

OVERWRITE = False

def _img_filename_prefix(chessboard_img_path):
    """ part of the image filename that shows which piece is on which square:
        RRqpBnNr-QKPkrQPK-PpbQnNB1-nRRBpNpk-Nqprrpqp-kKKbNBPP-kQnrpkrn-BKRqbbBp
    """
    return chessboard_img_path.split("/")[4][:-4]

def _img_sub_dir(chessboard_img_path):
    """ The sub-directory where the chessboard tile images will be saved
    """
    sub_dir = chessboard_img_path.split("/")[3]
    return os.path.join(TILES_DIR, sub_dir)

def _img_save_dir(chessboard_img_path):
    """ The directory within the sub-directory that will contain the
        tile images
    """
    return os.path.join(
        _img_sub_dir(chessboard_img_path),
        _img_filename_prefix(chessboard_img_path),
    )

def save_tiles(tiles, chessboard_img_path):
    """ Saves all 64 tiles as 32x32 PNG files with this naming convention:

        a1_R.png (white rook on a1)
        d8_q.png (black queen on d8)
        c4_1.png (nothing on c4)
    """
    sub_dir = _img_sub_dir(chessboard_img_path)
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)
    img_save_dir = _img_save_dir(chessboard_img_path)
    print("\tSaving tiles to {}\n".format(img_save_dir))
    if not os.path.exists(img_save_dir):
        os.makedirs(img_save_dir)
    piece_positions = _img_filename_prefix(chessboard_img_path).split('-')
    files = 'abcdefgh'
    for i in range(64):
        piece = piece_positions[math.floor(i / 8)][i % 8]
        sqr_id = '{}{}'.format(files[i % 8], 8 - math.floor(i / 8))
        tile_img_filename = '{}/{}_{}.png'.format(img_save_dir, sqr_id, piece)
        tiles[i].save(tile_img_filename, format='PNG')

def generate_tiles_from_all_chessboards():
    """ Generates 32x32 PNGs for each square of all chessboards
        in CHESSBOARDS_DIR
    """
    if not os.path.exists(TILES_DIR):
        os.makedirs(TILES_DIR)
    chessboard_img_filenames = glob("{}/*/*.png".format(CHESSBOARDS_DIR))
    num_chessboards = len(chessboard_img_filenames)
    num_success = 0
    num_skipped = 0
    num_failed = 0
    for i, chessboard_img_path in enumerate(chessboard_img_filenames):
        print("%3d/%d %s" % (i + 1, num_chessboards, chessboard_img_path))
        img_save_dir = _img_save_dir(chessboard_img_path)
        if os.path.exists(img_save_dir) and not OVERWRITE:
            print("\tIgnoring existing {}\n".format(img_save_dir))
            num_skipped += 1
            continue
        tiles = get_chessboard_tiles(chessboard_img_path, use_grayscale=USE_GRAYSCALE)
        if len(tiles) != 64:
            print("\t!! Expected 64 tiles. Got {}\n".format(len(tiles)))
            num_failed += 1
            continue
        save_tiles(tiles, chessboard_img_path)
        num_success += 1
    print(
        'Processed {} chessboard images ({} generated, {} skipped, {} failed)'.format(
            num_chessboards, num_success, num_skipped, num_failed
        )
    )

if __name__ == '__main__':
    np.set_printoptions(suppress=True, precision=2)
    generate_tiles_from_all_chessboards()
