# Chessboard recognizer

Uses a convolutional neural network to recognize the position of pieces
on a chessboard image.

If you have an image of a chessboard in `chessboard.png`

<img src="https://user-images.githubusercontent.com/208617/69907303-d526b400-13a0-11ea-982f-47dc7cacecdc.png" width=320 />

Run the program like this

`./recognize.py chessboard.png`

To get the chessboard position in [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) notation

`111rkb1r/1pp11ppp/11n1q1n1/p111Pb11/11Pp1111/PN111NB1/1P1QPPPP/111RKB1R`

## Getting started

Training and using the neural network requires [Tensorflow 2](https://www.tensorflow.org/)
With python3 installed, set up your virtualenv and install python dependencies
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

To download a bunch of images with pieces randomly placed on chessboards:
`./generate_chessboards.py`

To convert these downloaded chessboard images into 32x32 PNGs used for training:
`./generate_tiles.py`

To view generated chessboards and tiles
`./view_images.py`

# Acknowledgements

* https://github.com/Elucidation/tensorflow_chessbot
