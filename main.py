# -*- coding: utf-8 -*-
"""multiclassskincancer.ipynb

Automatically generated by Colaboratory.


"""

from google.colab import drive

drive.mount('/content/drive')

import numpy as np
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications
from keras.utils.np_utils import to_categorical
import matplotlib.pyplot as plt
import math
import cv2
from keras.optimizers import Adam

img_width, img_height = 224, 224

top_model_weights_path = 'bottleneck_fc_model.h5'
train_data_dir = '/content/drive/My Drive/Colab Notebooks/cancerimagesTRAINING'
validation_data_dir = '/content/drive/My Drive/Colab Notebooks/cancerimagesVALIDATION'

epochs = 30

batch_size = 16

model = applications.VGG16(include_top=False, weights='imagenet')

datagen = ImageDataGenerator(rescale=1. / 255)

generator = datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode=None,
    shuffle=False)

nb_train_samples = len(generator.filenames)
num_classes = len(generator.class_indices)

predict_size_train = int(math.ceil(nb_train_samples / batch_size))

bottleneck_features_train = model.predict_generator(
    generator, predict_size_train)

np.save('bottleneck_features_train.npy', bottleneck_features_train)

generator = datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode=None,
    shuffle=False)

nb_validation_samples = len(generator.filenames)

predict_size_validation = int(math.ceil(nb_validation_samples / batch_size))

bottleneck_features_validation = model.predict_generator(
    generator, predict_size_validation)

np.save('bottleneck_features_validation.npy', bottleneck_features_validation)

datagen_top = ImageDataGenerator(rescale=1. / 255)
generator_top = datagen_top.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False)

nb_train_samples = len(generator_top.filenames)
num_classes = len(generator_top.class_indices)

train_data = np.load('bottleneck_features_train.npy')

train_labels = generator_top.classes

train_labels = to_categorical(train_labels, num_classes=num_classes)

generator_top = datagen_top.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode=None,
    shuffle=False)

nb_validation_samples = len(generator_top.filenames)

validation_data = np.load('bottleneck_features_validation.npy')

validation_labels = generator_top.classes
validation_labels = to_categorical(validation_labels, num_classes=num_classes)

model = Sequential()
model.add(Flatten(input_shape=train_data.shape[1:]))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

optimizer = Adam(lr=0.0001)
model.compile(loss='categorical_crossentropy',
              optimizer=optimizer,
              metrics=['accuracy'])

history = model.fit(train_data, train_labels,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_data=(validation_data, validation_labels))

model.save_weights(top_model_weights_path)

(eval_loss, eval_accuracy) = model.evaluate(
    validation_data, validation_labels, batch_size=batch_size, verbose=1)

plt.subplot(211)
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')

plt.subplot(212)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

from google.colab.patches import cv2_imshow

image_path = '/content/drive/My Drive/Colab Notebooks/cancerimagesTRAINING/squamouscellcarcinoma/ISIC_0024575.jpg'
orig = cv2.imread(image_path)

print("[INFO] loading and preprocessing image...")
image = load_img(image_path, target_size=(224, 224))
image = img_to_array(image)

image = image / 255

image = np.expand_dims(image, axis=0)

model = applications.VGG16(include_top=False, weights='imagenet')

bottleneck_prediction = model.predict(image)

#neural net layers
model = Sequential()
model.add(Flatten(input_shape=bottleneck_prediction.shape[1:]))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='sigmoid'))

model.load_weights(top_model_weights_path)


#predictions
class_predicted = model.predict_classes(bottleneck_prediction)

inID = class_predicted[0]

class_dictionary = generator_top.class_indices

inv_map = {v: k for k, v in class_dictionary.items()}

label = inv_map[inID]

print("Image ID: {}, Label/ ACTUAL TYPE OF SKIN CANCER: {}".format(inID, label))

cv2.putText(orig, "Predicted: {}".format(label), (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (43, 99, 255), 2)
plt.imshow(orig)