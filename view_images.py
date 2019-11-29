#!/usr/bin/env python3

from glob import glob

from constants import CHESSBOARDS_DIR, TILES_DIR

OUT_FILE = 'tiles.html'

css = '''
  body {
    font-family: sans-serif;
  }

  .fen-char {
    display: inline-block;
    width: 20px;
  }
'''

if __name__ == '__main__':
    print('Found {} tile images'.format(len(glob(TILES_DIR + '/*/*.png'))))
    tile_dirs = glob(TILES_DIR + '/*')
    with open(OUT_FILE, 'w') as f:
        f.write('<html lang="en">')
        f.write('<style>{}</style>'.format(css))
        for tile_dir in tile_dirs:
            prefix = tile_dir.replace(TILES_DIR + '/', '')
            chessboard_img_path = '{}/{}.png'.format(CHESSBOARDS_DIR, prefix)
            f.write('<h3>{}</h3>'.format(chessboard_img_path))
            f.write('<img src="{}"/>'.format(chessboard_img_path))
            f.write('<h3>{}</h3>'.format(tile_dir))
            square_map = {}
            for tile_img_path in sorted(glob('{}/*.png'.format(tile_dir))):
                square_id = tile_img_path[-8:-6]
                fen_char = tile_img_path[-5]
                square_map[square_id] = {
                    'img_src': tile_img_path,
                    'fen_char': fen_char,
                }
            for rank in [8,7,6,5,4,3,2,1]:
                for file in ['a','b','c','d','e','f','g','h']:
                    square_id = '{}{}'.format(file, rank)
                    f.write('<img src="{}"/>'.format(square_map[square_id]['img_src']))
                    f.write('<span class="fen-char">{}</span>'.format(square_map[square_id]['fen_char']))
                f.write('<br>')
            f.write('<br>')
        f.write('</html>')
    print('Open {} to view all tile images'.format(OUT_FILE))
