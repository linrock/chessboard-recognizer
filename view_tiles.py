from glob import glob

if __name__ == '__main__':
    with open("train_tiles.html", "w") as f:
        for img_path in glob("./train_tiles/*/*.png"):
            f.write('<img src="{}"/>'.format(img_path))
            f.write(img_path[-8:-4])
            f.write('<br>')

    print("Written to train_tiles.html")
