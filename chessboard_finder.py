#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pass in image of online chessboard screenshot, returns corners of chessboard
# usage: chessboard_finder.py [-h] urls [urls ...]

# Find orthorectified chessboard corners in image

# positional arguments:
#   urls        Input image urls

# optional arguments:
#   -h, --help  show this help message and exit

import numpy as np
import PIL.Image

def _get_all_sequences(seq, min_seq_len=7, err_px=5):
    """ Given sequence of increasing numbers, get all sequences with common
        spacing (within err_px) that contain at least min_seq_len values
    """
    # Sanity check that there are enough values to satisfy
    if len(seq) < min_seq_len:
        return []

    # For every value, take the next value and see how many times we can step
    # that falls on another value within err_px points
    seqs = []
    for i in range(len(seq)-1):
        for j in range(i+1, len(seq)):
            # Check that seq[i], seq[j] not already in previous sequences
            duplicate = False
            for prev_seq in seqs:
                for k in range(len(prev_seq)-1):
                    if seq[i] == prev_seq[k] and seq[j] == prev_seq[k+1]:
                        duplicate = True
            if duplicate:
                continue
            d = seq[j] - seq[i]
            
            # Ignore two points that are within error bounds of each other
            if d < err_px:
                continue

            s = [seq[i], seq[j]]
            n = s[-1] + d
            while np.abs((seq-n)).min() < err_px:
                n = seq[np.abs((seq-n)).argmin()]
                s.append(n)
                n = s[-1] + d

            if len(s) >= min_seq_len:
                s = np.array(s)
                seqs.append(s)
    return seqs

def _nonmax_suppress_1d(arr, winsize=5):
    """ Return 1d array with only peaks, use neighborhood window of winsize px
    """
    _arr = arr.copy()
    for i in range(_arr.size):
        if i == 0:
            left_neighborhood = 0
        else:
            left_neighborhood = arr[max(0,i-winsize):i]
        if i >= _arr.size-2:
            right_neighborhood = 0
        else:
            right_neighborhood = arr[i+1:min(arr.size-1,i+winsize)]

        if arr[i] < np.max(left_neighborhood) or arr[i] <= np.max(right_neighborhood):
            _arr[i] = 0
    return _arr

def detect_chessboard_corners(img_arr_gray, noise_threshold = 8000):
    """ Load image grayscale as an numpy array
        Return None on failure to find a chessboard

        noise_threshold: Ratio of standard deviation of hough values along an axis
        versus the number of pixels, manually measured bad trigger images
        at < 5,000 and good  chessboards values at > 10,000
    """
    # Get gradients, split into positive and inverted negative components 
    gx, gy = np.gradient(img_arr_gray)
    gx_pos = gx.copy()
    gx_pos[gx_pos<0] = 0
    gx_neg = -gx.copy()
    gx_neg[gx_neg<0] = 0

    gy_pos = gy.copy()
    gy_pos[gy_pos<0] = 0
    gy_neg = -gy.copy()
    gy_neg[gy_neg<0] = 0

    # 1-D ampltitude of hough transform of gradients about X & Y axes
    num_px = img_arr_gray.shape[0] * img_arr_gray.shape[1]
    hough_gx = gx_pos.sum(axis=1) * gx_neg.sum(axis=1)
    hough_gy = gy_pos.sum(axis=0) * gy_neg.sum(axis=0)

    # Check that gradient peak signal is strong enough by
    # comparing normalized standard deviation to threshold
    if min(hough_gx.std() / hough_gx.size,
           hough_gy.std() / hough_gy.size) < noise_threshold:
      return None
    
    # Normalize and skeletonize to just local peaks
    hough_gx = _nonmax_suppress_1d(hough_gx) / hough_gx.max()
    hough_gy = _nonmax_suppress_1d(hough_gy) / hough_gy.max()

    # Arbitrary threshold of 20% of max
    hough_gx[hough_gx<0.2] = 0
    hough_gy[hough_gy<0.2] = 0

    # Now we have a set of potential vertical and horizontal lines that
    # may contain some noisy readings, try different subsets of them with
    # consistent spacing until we get a set of 7, choose strongest set of 7
    pot_lines_x = np.where(hough_gx)[0]
    pot_lines_y = np.where(hough_gy)[0]
    pot_lines_x_vals = hough_gx[pot_lines_x]
    pot_lines_y_vals = hough_gy[pot_lines_y]

    # Get all possible length 7+ sequences
    seqs_x = _get_all_sequences(pot_lines_x)
    seqs_y = _get_all_sequences(pot_lines_y)
    
    if len(seqs_x) == 0 or len(seqs_y) == 0:
        return None
    
    # Score sequences by the strength of their hough peaks
    seqs_x_vals = [pot_lines_x_vals[[v in seq for v in pot_lines_x]] for seq in seqs_x]
    seqs_y_vals = [pot_lines_y_vals[[v in seq for v in pot_lines_y]] for seq in seqs_y]

    # shorten sequences to up to 9 values based on score
    # X sequences
    for i in range(len(seqs_x)):
        seq = seqs_x[i]
        seq_val = seqs_x_vals[i]

        # if the length of sequence is more than 7 + edges = 9
        # strip weakest edges 
        if len(seq) > 9:
            # while not inner 7 chess lines, strip weakest edges
            while len(seq) > 7:
              if seq_val[0] > seq_val[-1]:
                  seq = seq[:-1]
                  seq_val = seq_val[:-1]
              else:
                  seq = seq[1:]
                  seq_val = seq_val[1:]

        seqs_x[i] = seq
        seqs_x_vals[i] = seq_val

    # Y sequences
    for i in range(len(seqs_y)):
        seq = seqs_y[i]
        seq_val = seqs_y_vals[i]
        while len(seq) > 9:
            if seq_val[0] > seq_val[-1]:
                seq = seq[:-1]
                seq_val = seq_val[:-1]
            else:
                seq = seq[1:]
                seq_val = seq_val[1:]

        seqs_y[i] = seq
        seqs_y_vals[i] = seq_val

    # Now that we only have length 7-9 sequences, score and choose the best one
    scores_x = np.array([np.mean(v) for v in seqs_x_vals])
    scores_y = np.array([np.mean(v) for v in seqs_y_vals])

    # Keep first sequence with the largest step size
    # scores_x = np.array([np.median(np.diff(s)) for s in seqs_x])
    # scores_y = np.array([np.median(np.diff(s)) for s in seqs_y])

    # TODO (elucidation): Choose heuristic score between step size and hough response

    best_seq_x = seqs_x[scores_x.argmax()]
    best_seq_y = seqs_y[scores_y.argmax()]
    # print(best_seq_x, best_seq_y)

    # Now if we have sequences greater than length 7, (up to 9),
    # that means we have up to 9 possible combinations of sets of 7 sequences
    # We try all of them and see which has the best checkerboard response
    sub_seqs_x = [best_seq_x[k:k+7] for k in range(len(best_seq_x) - 7 + 1)]
    sub_seqs_y = [best_seq_y[k:k+7] for k in range(len(best_seq_y) - 7 + 1)]

    dx = np.median(np.diff(best_seq_x))
    dy = np.median(np.diff(best_seq_y))
    corners = np.zeros(4, dtype=int)
    
    # Add 1 buffer to include the outer tiles, since sequences are only using
    # inner chessboard lines
    corners[0] = int(best_seq_y[0]-dy)
    corners[1] = int(best_seq_x[0]-dx)
    corners[2] = int(best_seq_y[-1]+dy)
    corners[3] = int(best_seq_x[-1]+dx)

    # Generate crop image with on full sequence, which may be wider than a normal
    # chessboard by an extra 2 tiles, we'll iterate over all combinations
    # (up to 9) and choose the one that correlates best with a chessboard
    gray_img_crop = PIL.Image.fromarray(img_arr_gray).crop(corners)

    # Build a kernel image of an idea chessboard to correlate against
    k = 8 # Arbitrarily chose 8x8 pixel tiles for correlation image
    quad = np.ones([k,k])
    kernel = np.vstack([np.hstack([quad,-quad]), np.hstack([-quad,quad])])
    kernel = np.tile(kernel,(4,4)) # Becomes an 8x8 alternating grid (chessboard)
    kernel = kernel/np.linalg.norm(kernel) # normalize
    # 8*8 = 64x64 pixel ideal chessboard

    k = 0
    n = max(len(sub_seqs_x), len(sub_seqs_y))
    final_corners = None
    best_score = None

    # Iterate over all possible combinations of sub sequences and keep the corners
    # with the best correlation response to the ideal 64x64px chessboard
    for i in range(len(sub_seqs_x)):
        for j in range(len(sub_seqs_y)):
            k = k + 1
          
            # [y, x, y, x]
            sub_corners = np.array([
                sub_seqs_y[j][0]-corners[0]-dy, sub_seqs_x[i][0]-corners[1]-dx,
                sub_seqs_y[j][-1]-corners[0]+dy, sub_seqs_x[i][-1]-corners[1]+dx
            ], dtype=np.int)

            # Generate crop candidate, nearest pixel is fine for correlation check
            sub_img = gray_img_crop.crop(sub_corners).resize((64,64)) 

            # Perform correlation score, keep running best corners as our final output
            # Use absolute since it's possible board is rotated 90 deg
            score = np.abs(np.sum(kernel * sub_img))
            if best_score is None or score > best_score:
                best_score = score
                final_corners = sub_corners + [
                    corners[0], corners[1], corners[0], corners[1]
                ]
    return final_corners

def get_chessboard_corners(img_arr, detect_corners=False):
    """ Returns a tuple of (corners, error_message)
    """
    if not detect_corners:
        # Don't try to detect corners. Assume the entire image is a board
        return (([0, 0, img_arr.shape[0], img_arr.shape[1]]), None)
    corners = detect_chessboard_corners(img_arr)
    if corners is None:
        return (None, "Failed to find corners in chessboard image")
    width = corners[2] - corners[0]
    height = corners[3] - corners[1]
    ratio = abs(1 - width / height)
    if ratio > 0.05:
        return (corners, "Invalid corners - chessboard size is not square")
    if corners[0] > 1 or corners[1] > 1:
        # TODO generalize this for chessboards positioned within images
        return (corners, "Invalid corners - (x,y) are too far from (0,0)")
    return (corners, None)

