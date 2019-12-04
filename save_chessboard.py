#!/usr/bin/env python3

import sys
import re
import shutil
import os

""" Given a chessboard image with a known FEN, save it as
    an image used for training the neural net
"""
if __name__ == '__main__':
    chessboard_img_file_path = sys.argv[1]
    folder_prefix = sys.argv[2]
    correct_fen = sys.argv[3]

    filename_prefix = correct_fen.split(' ')[0]
    filename_prefix = filename_prefix.replace('/', '-')
    for digit in re.findall(r'[2-8]', filename_prefix):
        filename_prefix = filename_prefix.replace(digit, int(digit) * '1')
    new_file_name = "{}.png".format(filename_prefix)
    new_file_path = os.path.join(
        "images", "chessboards", folder_prefix, new_file_name
    )
    print("Copying {} to {}".format(chessboard_img_file_path, new_file_path))
    shutil.copyfile(chessboard_img_file_path, new_file_path)

