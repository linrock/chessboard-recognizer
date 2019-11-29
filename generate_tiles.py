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
import chessboard_finder

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
    letters = 'abcdefgh'
    for i in range(64):
        piece = piece_positions[math.floor(i / 8)][i % 8]
        sqr_id = '{}{}'.format(letters[i % 8], 8 - math.floor(i / 8))
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

def generate_tileset():
    # Create output folder as needed
    if not os.path.exists(TILES_DIR):
        os.makedirs(TILES_DIR)

    # Get all image files of type .png
    img_files = set(glob("%s/*.png" % CHESSBOARDS_DIR))

    num_success = 0
    num_failed = 0

    for i, img_path in enumerate(img_files):
        print("%3d/%d %s" % (i+1, len(img_files), img_path))
        img_filename_prefix = img_path[len(CHESSBOARDS_DIR):-4]
        if img_filename_prefix[0] == '/':
            img_filename_prefix = img_filename_prefix[1:]

        # Create output save directory or skip this image if it exists
        img_save_dir = '{}/{}'.format(TILES_DIR, img_filename_prefix)
        
        # Load image
        img = PIL.Image.open(img_path)
        img_arr = np.array(img, dtype=np.float32)

        # Get tiles
        corners = chessboard_finder.find_chessboard_corners(img_arr)
        if corners is None:
            print("\t!! Failed to find corners in chessboard image\n")
            num_failed += 1
            continue
        print("\tFound corners: {}".format(corners))
        width = corners[2] - corners[0]
        height = corners[3] - corners[1]
        ratio = abs(1 - width / height)
        if ratio > 0.05:
            print("\t!! Invalid corners - chessboard size is not square\n")
            num_failed += 1
            continue
        if corners[0] > 1 or corners[1] > 1:
            # TODO generalize this for chessboards positioned within images
            print("\t!! Invalid corners - (x,y) are too far from (0,0)\n")
            num_failed += 1
            continue
        # Save tiles
        tiles = chessboard_finder.get_chess_tiles_gray(img_arr, corners)
        if len(tiles) > 0:
            print("\tSaving tiles to {}\n".format(img_save_dir))
            save_tiles(tiles, img_save_dir, img_filename_prefix)
            num_success += 1

    print(
        'Processed {} chessboard images ({} generated, {} failed)'.format(
            len(img_files), num_success, num_failed
        )
    )

if __name__ == '__main__':
    np.set_printoptions(suppress=True, precision=2)
    generate_tileset()
