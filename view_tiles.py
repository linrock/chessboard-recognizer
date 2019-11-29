from glob import glob

OUT_FILE = 'tiles.html'

TILES_DIR = './images/tiles'
CHESSBOARDS_DIR = './images/chessboards'

if __name__ == '__main__':
    print('Found {} tile images'.format(len(glob(TILES_DIR + '/*/*.png'))))
    tile_dirs = glob(TILES_DIR + '/*')
    with open(OUT_FILE, 'w') as f:
        f.write('<html lang="en">')
        for tile_dir in tile_dirs:
            prefix = tile_dir.replace(TILES_DIR + '/', '')
            chessboard_img_path = '{}/{}.png'.format(CHESSBOARDS_DIR, prefix)
            f.write('<h3>{}</h3>'.format(chessboard_img_path))
            f.write('<img src="{}"/>'.format(chessboard_img_path))
            f.write('<h3>{}</h3>'.format(tile_dir))
            for tile_img_path in sorted(glob('{}/*.png'.format(tile_dir))):
                f.write('<img src="{}"/>'.format(tile_img_path))
                f.write(tile_img_path[-8:-4])
                f.write('<br>')
        f.write('</html>')
    print('Open {} to view all tile images'.format(OUT_FILE))
