import numpy as np
import PIL.Image

def _get_resized_chessboard(img_arr, corners):
    """ img_arr = numpy array of RGB image data (dims: WxHx3)
        corners = (x0, y0, x1, y1), where (x0, y0) is top-left corner
                                          (x1, y1) is bottom-right corner
        Returns a 256x256 image of a chessboard (32x32 per tile)
    """
    height, width, depth = img_arr.shape
    assert depth == 3, "Need RGB color image input"

    # corners could be outside image bounds, pad image as needed
    padl_x = max(0, -corners[0])
    padl_y = max(0, -corners[1])
    padr_x = max(0, corners[2] - width)
    padr_y = max(0, corners[3] - height)

    img_padded = np.pad(
        img_arr,
        ((padl_y, padr_y), (padl_x, padr_x), (0, 0)),
        mode='edge'
    )
    chessboard_img = img_padded[
        (padl_y + corners[1]):(padl_y + corners[3]),
        (padl_x + corners[0]):(padl_x + corners[2]),
        :
    ]
    img_data = PIL.Image.fromarray(chessboard_img)
    return img_data.resize([256, 256], PIL.Image.BILINEAR)

def get_img_arr(chessboard_img_path):
    img = PIL.Image.open(chessboard_img_path).convert('RGB')
    return np.array(img, dtype=np.uint8)

def get_chessboard_tiles(img_arr, corners, use_grayscale=True):
    """ img_arr = a 32x32 numpy array from a color RGB image
        corners = (x0, y0, x1, y1) for top-left and bottom-right corner
        use_grayscale = true/false for whether to return tiles in grayscale
    """
    img_data = _get_resized_chessboard(img_arr, corners)
    if use_grayscale:
        img_data = img_data.convert('L', (0.2989, 0.5870, 0.1140, 0))
    chessboard_256x256_img = np.asarray(img_data, dtype=np.uint8)
    # 64 tiles in order from top-left to bottom-right (A8, B8, ..., G1, H1)
    tiles = [None] * 64
    for rank in range(8): # rows/ranks (numbers)
        for file in range(8): # columns/files (letters)
            sq_i = rank * 8 + file
            tiles[sq_i] = np.zeros([32, 32, 3], dtype=np.uint8)
            for i in range(32):
                for j in range(32):
                    if use_grayscale:
                        tiles[sq_i][i, j] = chessboard_256x256_img[
                            rank*32 + i,
                            file*32 + j,
                        ]
                    else:
                        tiles[sq_i][i, j] = chessboard_256x256_img[
                            rank*32 + i,
                            file*32 + j,
                            :,
                        ]
    return tiles

def tile_image_data(tile):
    """ Returns 32x32 tile image data from np array matrix
    """
    return PIL.Image.fromarray(tile, 'RGB').resize([32, 32], PIL.Image.ADAPTIVE)
