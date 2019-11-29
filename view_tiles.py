from glob import glob

OUT_FILE = 'tiles.html'

if __name__ == '__main__':
    print('Found {} tile images'.format(len(glob('./images/tiles/*/*.png'))))
    tile_dirs = glob('./images/tiles/*')
    with open(OUT_FILE, 'w') as f:
        f.write('<html lang="en">')
        for tile_dir in tile_dirs:
            f.write('<h2>{}</h2>'.format(tile_dir))
            for img_path in glob('{}/*.png'.format(tile_dir)):
                f.write('<img src="{}"/>'.format(img_path))
                f.write(img_path[-8:-4])
                f.write('<br>')
        f.write('</html>')
    print('Open {} to view all tile images'.format(OUT_FILE))
