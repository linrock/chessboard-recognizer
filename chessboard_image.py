import numpy as np
import PIL.Image

def _get_chessboard_gray(img_arr, corners):
    """ img_arr = a grayscale image
        corners = (x0, y0, x1, y1), where (x0, y0) is top-left corner
                                          (x1, y1) is bottom-right corner
        Returns a 256x256 normalized grayscale image of a chessboard
        (32x32 per tile)
    """
    height, width, depth = img_arr.shape
    assert depth == 3, "Need RGB color image input"

    # corners could be outside image bounds, pad image as needed
    padl_x = max(0, -corners[0])
    padl_y = max(0, -corners[1])
    padr_x = max(0, corners[2] - width)
    padr_y = max(0, corners[3] - height)

    img_padded = np.pad(img_arr, ((padl_y, padr_y), (padl_x, padr_x), (0, 0)), mode='edge')

    chessboard_img = img_padded[
        (padl_y + corners[1]):(padl_y + corners[3]),
        (padl_x + corners[0]):(padl_x + corners[2])
    ]
    # 256x256px image, 32x32px individual tiles
    chessboard_img_resized = np.asarray(
        PIL.Image.fromarray(chessboard_img)
           .resize([256, 256], PIL.Image.BILINEAR)
           .convert('L', (0.2989, 0.5870, 0.1140, 0)),
        dtype=np.uint8,
    )
    return chessboard_img_resized

def get_img_arr(chessboard_img_path):
    img = PIL.Image.open(chessboard_img_path).convert('RGB')
    return np.array(img, dtype=np.uint8)

def get_chessboard_tiles_color(img_arr, corners):
    """ img_arr = a 32x32 numpy array from a color RGB image
        corners = (x0, y0, x1, y1) for top-left and bottom-right corner
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
        ((padl_y, padr_y), (padl_x, padr_x), (0,0)),
        mode='edge'
    )
    chessboard_img = img_padded[
        (padl_y + corners[1]):(padl_y + corners[3]), 
        (padl_x + corners[0]):(padl_x + corners[2]),
        :
    ]

    # 256x256 px RGB image, 32x32px individual RGB tiles
    chessboard_img_resized = np.asarray(
        PIL.Image
          .fromarray(chessboard_img, 'RGB')
          .resize([256, 256], PIL.Image.BILINEAR),
        dtype=np.uint8,
    )
    tiles = [None] * 64
    for rank in range(8): # rows/ranks (numbers)
        for file in range(8): # columns/files (letters)
            tiles[rank*8+file] = np.zeros([32, 32, 3], dtype=np.uint8)
            for i in range(32):
               for j in range(32):
                  for k in range(3):
                      tiles[rank*8+file][i, j, k] = chessboard_img_resized[
                          rank*32 + i,
                          file*32 + j,
                          k,
                      ]
    return tiles

def get_chessboard_tiles_gray(img_arr, corners):
    """ Given an array of values representing a chessboard, first convert to
        a 256x256 normalized grayscale image of a chessboard (32x32 per tile),
        then return a 32x32x64 tile array
    """
    processed_gray_img = _get_chessboard_gray(img_arr, corners)
    # stack deep 64 tiles
    # order start from top-left to bottom right is A8, B8, ...
    tiles = [None] * 64
    for rank in range(8): # rows/ranks (numbers)
        for file in range(8): # columns/files (letters)
            tiles[rank*8+file] = np.zeros([32, 32, 3], dtype=np.uint8)
            for i in range(32):
                for j in range(32):
                    tiles[rank*8+file][i, j, k] = processed_gray_img[
                        rank*32 + i,
                        file*32 + j,
                    ]
    return tiles

