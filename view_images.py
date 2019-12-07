#!/usr/bin/env python3

import sys
import os
from glob import glob

from constants import CHESSBOARDS_DIR, TILES_DIR

OUT_FILE = 'images.html'

if __name__ == '__main__':
    sub_dir = sys.argv[1] if len(sys.argv) > 1 else '*'
    tiles_base_dir = os.path.join(TILES_DIR, sub_dir, '*')
    print('Looking for tile images in {}'.format(tiles_base_dir))
    print('Found {} tile images'.format(len(glob(os.path.join(tiles_base_dir, '*.png')))))
    tile_dirs = glob(tiles_base_dir)
    with open(OUT_FILE, 'w') as f:
        f.write('<html lang="en">')
        f.write('<link rel="stylesheet" href="./web/style.css" />')
        for tile_dir in tile_dirs:
            img_dir = tile_dir.split('/')[-2]
            img_filename_prefix = tile_dir.split('/')[-1]
            chessboard_img_path = os.path.join(
                CHESSBOARDS_DIR, img_dir, '{}.png'.format(img_filename_prefix)
            )
            f.write('<h3>{}</h3>'.format(chessboard_img_path))
            f.write('<img src="{}" width="256"/>'.format(chessboard_img_path))
            f.write('<h3>{}</h3>'.format(tile_dir))
            square_map = {}
            for tile_img_path in glob(os.path.join(tile_dir, '*.png')):
                square_id = tile_img_path[-8:-6]
                fen_char = tile_img_path[-5]
                square_map[square_id] = {
                    'img_src': tile_img_path,
                    'fen_char': fen_char,
                }
            for rank in [8,7,6,5,4,3,2,1]:
                for file in ['a','b','c','d','e','f','g','h']:
                    square_id = '{}{}'.format(file, rank)
                    fen_char = square_map[square_id]['fen_char']
                    f.write('<img src="{}"/>'.format(square_map[square_id]['img_src']))
                    f.write('<span class="fen-char {}">{}</span>'.format(
                        'empty' if fen_char is '1' else '',
                        fen_char
                    ))
                f.write('<br>')
            f.write('<br>')
        f.write('</html>')
    print('Open {} to view all tile images'.format(OUT_FILE))
