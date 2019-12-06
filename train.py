#!/usr/bin/env python3

import os
from glob import glob
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

from constants import TILES_DIR, NN_MODEL_PATH, FEN_CHARS, USE_GRAYSCALE

RATIO = 0.82    # ratio of training vs. test data
N_EPOCHS = 20

def image_data(image_path) -> tf.image:
    n_channels = 1 if USE_GRAYSCALE else 3
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=n_channels)
    img = tf.image.convert_image_dtype(img, tf.float32)
    return tf.image.resize(img, [32, 32])

def create_model() -> models.Sequential:
    """ Convolutional neural network for image classification.
        Same architecture as:
        https://www.tensorflow.org/tutorials/images/cnn
    """
    input_shape = (32, 32, 1) if USE_GRAYSCALE else (32, 32, 3)
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(len(FEN_CHARS), activation='softmax'),
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model

def get_dataset():
    """ Prepares training and test datasets from all PNG tiles
        in TILES_DIR
    """
    all_paths = np.array(glob('{}/*/*/*.png'.format(TILES_DIR)))
    np.random.seed(1)
    np.random.shuffle(all_paths)

    divider = int(len(all_paths) * RATIO)
    train_paths = all_paths[:divider]
    test_paths = all_paths[divider:]

    # TODO why does a list comprehension with np.array freeze??
    train_images = []
    train_labels = []
    for image_path in train_paths:
        piece_type = image_path[-5]
        assert piece_type in FEN_CHARS
        train_images.append(np.array(image_data(image_path)))
        train_labels.append(FEN_CHARS.index(piece_type))
    train_images = np.array(train_images)
    train_labels = np.array(train_labels)
    print("Loaded {} training images and labels".format(len(train_paths)))

    test_images = []
    test_labels = []
    for image_path in test_paths:
        piece_type = image_path[-5]
        assert piece_type in FEN_CHARS
        test_images.append(np.array(image_data(image_path)))
        test_labels.append(FEN_CHARS.index(piece_type))
    test_images = np.array(test_images)
    test_labels = np.array(test_labels)
    print("Loaded {} test images and labels".format(len(test_paths)))
    return ((train_images, train_labels), (test_images, test_labels))


if __name__ == '__main__':
    print('Tensorflow {}'.format(tf.version.VERSION))

    (train_images, train_labels), (test_images, test_labels) = get_dataset()
    if not len(train_images):
        print("No training images found!")
        exit(1)
    model = create_model()
    model.fit(train_images, train_labels, epochs=N_EPOCHS,
              validation_data=(test_images, test_labels))

    print('Saving CNN model to {}'.format(NN_MODEL_PATH))
    models.save_model(model, NN_MODEL_PATH, overwrite=True)

    print('Evaluating CNN model on test data:')
    test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=1)
