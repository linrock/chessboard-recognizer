# Chessboard recognizer

Uses a convolutional neural network to recognize the position of pieces
on a chessboard image.

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
