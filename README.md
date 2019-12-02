# Chessboard recognizer

Uses a convolutional neural network to recognize the positions of pieces
on a chessboard image.

If you have an image of a chessboard in `chessboard.png`

<img src="https://user-images.githubusercontent.com/208617/69907303-d526b400-13a0-11ea-982f-47dc7cacecdc.png" width=240 />

Run the program like this

`./recognize.py chessboard.png`

To get the chessboard position in [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) notation

`111rkb1r/1pp11ppp/11n1q1n1/p111Pb11/11Pp1111/PN111NB1/1P1QPPPP/111RKB1R`

## Sample results

Chess puzzle from a book:

<img src="https://user-images.githubusercontent.com/208617/69923373-5437ed00-1472-11ea-9877-89503cc532ea.png" width=240 />

Predicted: [11r11k1r/111111bp/p111q111/1111pp1Q/1p1n11P1/N1111111/PPP111BP/11KR1R11](https://lichess.org/analysis/standard/11r11k1r/111111bp/p111q111/1111pp1Q/1p1n11P1/N1111111/PPP111BP/11KR1R11) (99.633% confidence)

Lichess analysis board diagram with arrows:

<img src="https://user-images.githubusercontent.com/208617/69923935-4ab08400-1476-11ea-8a65-5e11f0145b28.png" width=240 />


Predicted: [11111r1k/11q1r1pp/11p1111n/11P11B11/pPQ1pR11/P11111P1/1111R11P/1111111K](https://lichess.org/analysis/standard/11111r1k/11q1r1pp/11p1111n/11P11B11/pPQ1pR11/P11111P1/1111R11P/1111111K) (99.997% confidence)

## Getting started

You'll need python 3 and [Tensorflow 2](https://www.tensorflow.org/)

Set up your virtualenv and install python dependencies
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

You'll need a neural network model to use `./recognize.py`

To use a pre-trained model, download [nn-model.zip](https://github.com/linrock/chessboard-recognizer/releases/download/v0.1/nn-model.zip) and unzip in the project root folder.

To train your own model, you'll need lots of images of chess pieces

You can download [training-images.zip](https://github.com/linrock/chessboard-recognizer/releases/download/v0.1/training-images.zip) and unzip in the project root folder for the images used for the pre-trained model.

Or you can generate your own training images with these scripts:

* `./generate_chessboards.py` downloads a bunch of chessboard images with randomly-placed pieces
* `./generate_tiles.py` converts these downloaded chessboard images into 32x32 PNGs used for training
* `./view_images.py` for a convenient way to manually verify the generated images

Once you have a neural network model ready, run `./recognize.py` with a path to a chessboard image:

`./recognize.py ~/Desktop/chessboard.png`

# Acknowledgements

* Original inspiration from [tensorflow_chessbot](https://github.com/Elucidation/tensorflow_chessbot) by [Elucidation](https://github.com/Elucidation)
* Neural network architecture from https://www.tensorflow.org/tutorials/images/cnn
