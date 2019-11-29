import os
from glob import glob
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

RATIO = 0.8                 # ratio of training vs. test data
LABELS = 'RNBQKPrnbqkp1'    # 13 labels for possible square contents

def image_data(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    return tf.image.resize(img, [32, 32])

def create_model():
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(len(LABELS), activation='softmax'))
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model

def load_dataset():
    all_paths = np.array(glob("train_tiles/*/*.png"))
    np.random.seed(1)
    np.random.shuffle(all_paths)

    divider = int(len(all_paths) * RATIO)
    train_paths = all_paths[:divider]
    test_paths = all_paths[divider:]

    # TODO why does a list comprehension with np.array freeze??
    train_images = []
    train_labels = []
    for image_path in train_paths:
        train_images.append(np.array(image_data(image_path)))
        train_labels.append(LABELS.index(image_path[-5]))
    train_images = np.array(train_images)
    train_labels = np.array(train_labels)
    print("Loaded training images and labels")

    test_images = []
    test_labels = []
    for image_path in train_paths:
        test_images.append(np.array(image_data(image_path)))
        test_labels.append(LABELS.index(image_path[-5]))
    test_images = np.array(test_images)
    test_labels = np.array(test_labels)
    print("Loaded test images and labels")
    return ((train_images, train_labels), (test_images, test_labels))


if __name__ == '__main__':
    print('Tensorflow {}'.format(tf.version.VERSION))

    checkpoint_path = 'training/model.ckpt'
    checkpoint_dir = os.path.dirname(checkpoint_path)
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1)
    model = create_model()
    if Path('{}.index'.format(checkpoint_path)).is_file():
        print("Found checkpoint. Loading weights")
        model.load_weights(checkpoint_path)
    else:
        print("No checkpoint found. Training from scratch")

    (train_images, train_labels), (test_images, test_labels) = load_dataset()

    history = model.fit(train_images, train_labels, epochs=10,
                        validation_data=(test_images, test_labels),
                        callbacks=[cp_callback])

    print("Evaluating model on test data:")
    test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)
