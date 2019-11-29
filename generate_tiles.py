# usage: tileset_generator.py [-h] input_folder output_folder

# Generate tile images for alll chessboard images in input folder

# positional arguments:
#   input_folder   Input image folder
#   output_folder  Output tile folder

# optional arguments:
#   -h, --help     show this help message and exit

# Pass an input folder and output folder
# Builds tile images for each chessboard image in input folder and puts
# in the output folder
# Used for building training datasets
import os
from glob import glob
import argparse
import math

import numpy as np
import PIL.Image

from constants import CHESSBOARDS_DIR, TILES_DIR
from chessboard_finder import detect_chessboard_corners
from chessboard_image import get_img_arr, get_chessboard_tiles_gray

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
        if tiles.shape != (32, 32, 64):
            PIL.Image.fromarray(tiles[:, :, i]) \
                .resize([32, 32], PIL.Image.ADAPTIVE) \
                .save(tile_img_filename)
        else:
          # Possibly saving floats 0-1 needs to change fromarray settings
          PIL.Image.fromarray(
              (tiles[:,:,i] * 255).astype(np.uint8)
          ).save(tile_img_filename)

def get_chessboard_corners(img_arr, detect_corners=True):
    """ Returns a tuple of (corners, error_message)
    """
    if not detect_corners:
        # Don't try to detect corners. Assume the entire image is a board
        return (([0, 0, img_arr.shape[0], img_arr.shape[1]]), None)
    corners = detect_chessboard_corners(img_arr)
    if corners is None:
        return (None, "Failed to find corners in chessboard image")
    width = corners[2] - corners[0]
    height = corners[3] - corners[1]
    ratio = abs(1 - width / height)
    if ratio > 0.05:
        return (corners, "Invalid corners - chessboard size is not square")
    if corners[0] > 1 or corners[1] > 1:
        # TODO generalize this for chessboards positioned within images
        return (corners, "Invalid corners - (x,y) are too far from (0,0)")
    return (corners, None)

def generate_tileset():
    if not os.path.exists(TILES_DIR):
        os.makedirs(TILES_DIR)
    chessboard_img_filenames = set(glob("%s/*.png" % CHESSBOARDS_DIR))
    num_chessboards = len(chessboard_img_filenames)
    num_success = 0
    num_failed = 0
    for i, chessboard_img_path in enumerate(chessboard_img_filenames):
        print("%3d/%d %s" % (i+1, num_chessboards, chessboard_img_path))
        img_arr = get_img_arr(chessboard_img_path)
        (corners, error_message) = get_chessboard_corners(img_arr)
        if corners is not None:
            print("\tFound corners: {}".format(corners))
        if error_message:
            print("\t{}\n".format(error_message))
            num_failed += 1
            continue
        tiles = get_chessboard_tiles_gray(img_arr, corners)
        if tiles.shape != (32, 32, 64):
            print("\t!! Expected 64 tiles. Got {}\n".format(tiles.shape[2]))
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
    generate_tileset()
