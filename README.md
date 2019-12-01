# Chessboard recognizer

Uses a convolutional neural network to recognize the positions of pieces
on a chessboard image.

If you have an image of a chessboard in `chessboard.png`

<img src="https://user-images.githubusercontent.com/208617/69907303-d526b400-13a0-11ea-982f-47dc7cacecdc.png" width=300 />

Run the program like this

`./recognize.py chessboard.png`

To get the chessboard position in [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) notation

`111rkb1r/1pp11ppp/11n1q1n1/p111Pb11/11Pp1111/PN111NB1/1P1QPPPP/111RKB1R`

## Getting started

You'll need python 3 and [Tensorflow 2](https://www.tensorflow.org/)

Set up your virtualenv and install python dependencies
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

You'll need a neural network model to use `./recognize.py`

To use a pre-trained model, download [nn-model.zip](https://github.com/linrock/chessboard-recognizer/releases/download/v0.1/nn-model.zip) and unzip in `./nn/`

To train your own model, you'll need lots of images of chess pieces

You can download [training-images.zip](https://github.com/linrock/chessboard-recognizer/releases/download/v0.1/training-images.zip) and unzip in `./images/` for the images used for the pre-trained model.

Or you can generate your own training images with these scripts:

* `./generate_chessboards.py` downloads a bunch of chessboard images with randomly-placed pieces
* `./generate_tiles.py` converts these downloaded chessboard images into 32x32 PNGs used for training
* `./view_images.py` for a convenient way to manually verify the generated images

Once you have a neural network model ready, run `./recognize.py` with a path to a chessboard image:

`./recognize.py ~/Desktop/chessboard.png`

# Acknowledgements

* Original inspiration from [tensorflow_chessbot](https://github.com/Elucidation/tensorflow_chessbot) by [Elucidation](https://github.com/Elucidation)
* Neural network architecture from https://www.tensorflow.org/tutorials/images/cnn
