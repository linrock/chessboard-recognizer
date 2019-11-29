import numpy as np
import PIL.Image

def _get_chessboard_gray(img_arr, corners):
    """ img_arr = a grayscale image
        corners = (x0, y0, x1, y1), where (x0, y0) is top-left corner
                                          (x1, y1) is bottom-right corner
        Returns a 256x256 normalized grayscale image of a chessboard (32x32 per tile)
    """
    height, width = img_arr.shape

    # corners could be outside image bounds, pad image as needed
    padl_x = max(0, -corners[0])
    padl_y = max(0, -corners[1])
    padr_x = max(0, corners[2] - width)
    padr_y = max(0, corners[3] - height)
    img_padded = np.pad(img_arr, ((padl_y, padr_y), (padl_x, padr_x)), mode='edge')

    chessboard_img = img_padded[
        (padl_y + corners[1]):(padl_y + corners[3]), 
        (padl_x + corners[0]):(padl_x + corners[2])
    ]
    # 256x256px image, 32x32px individual tiles
    # Normalized
    chessboard_img_resized = np.asarray( \
          PIL.Image.fromarray(chessboard_img) \
          .resize([256, 256], PIL.Image.BILINEAR), dtype=np.uint8) / 255.0
    return chessboard_img_resized

def get_img_arr(chessboard_img_path):
    img = PIL.Image.open(chessboard_img_path)
    return np.array(img, dtype=np.float32)

def get_chessboard_tiles_color(img_arr, corners):
    """ img_arr = a 32x32 numpy array from a color RGB image
        corners = (x0, y0, x1, y1) for top-left corner to bot-right corner of board
    """
    height, width, depth = img_arr.shape
    if depth != 3:
        print("Need RGB color image input")
        return None

    # corners could be outside image bounds, pad image as needed
    padl_x = max(0, -corners[0])
    padl_y = max(0, -corners[1])
    padr_x = max(0, corners[2] - width)
    padr_y = max(0, corners[3] - height)

    img_padded = np.pad(img_arr, ((padl_y,padr_y),(padl_x,padr_x), (0,0)), mode='edge')

    chessboard_img = img_padded[
      (padl_y + corners[1]):(padl_y + corners[3]), 
      (padl_x + corners[0]):(padl_x + corners[2]), :]

    # 256x256 px RGB image, 32x32px individual RGB tiles, normalized 0-1 floats
    chessboard_img_resized = np.asarray( \
          PIL.Image.fromarray(chessboard_img) \
          .resize([256,256], PIL.Image.BILINEAR), dtype=np.float32) / 255.0

    # stack deep 64 tiles with 3 channesl RGB each
    # so, first 3 slabs are RGB for tile A1, then next 3 slabs for tile A2 etc.
    tiles = np.zeros([32,32,3*64], dtype=np.float32) # color
    # Assume A1 is bottom left of image, need to reverse rank since images start
    # with origin in top left
    for rank in range(8): # rows (numbers)
        for file in range(8): # columns (letters)
            # color
            tiles[:,:,3*(rank*8+file):3*(rank*8+file+1)] = \
              chessboard_img_resized[(7-rank)*32:((7-rank)+1)*32,file*32:(file+1)*32]
    return tiles

def get_chessboard_tiles_gray(img_arr, corners):
    """ Given an array of values representing a chessboard, first convert to
        a 256x256 normalized grayscale image of a chessboard (32x32 per tile),
        then return a 32x32x64 tile array
        NOTE (values must be in range 0-1)
    """
    processed_gray_img = _get_chessboard_gray(img_arr, corners)
    # stack deep 64 tiles
    # order start from top-left to bottom right is A8, B8, ...
    tiles = np.zeros([32, 32, 64], dtype=np.float32) # grayscale
    for rank in range(8): # rows (numbers)
        for file in range(8): # columns (letters)
            tiles[:, :, (rank*8+file)] = \
              processed_gray_img[rank*32:(rank+1)*32, file*32:(file+1)*32]
    return tiles

