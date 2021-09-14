# 이미지를 사용한 다중 분류(실험 비교용)
import os
import tensorflow as tf
import keras_preprocessing
from keras_preprocessing import image
from keras_preprocessing.image import ImageDataGenerator


# 이미지 불러오기
up_dir = os.path.join('images/train/up')
down_dir = os.path.join('images/train/down')
nothing_dir = os.path.join('images/train/nothing')

up_files = os.listdir(up_dir)
down_files = os.listdir(down_dir)
nothing_files = os.listdir(nothing_dir)

print('Total number of training up images:', len(up_files))
print('Total number of training down images:', len(down_files))
print('Total number of training nothing images:', len(nothing_files))

# 학습
TRAINING_DIR = "images/train/"
training_datagen = ImageDataGenerator(
    rescale = 1./255,
    # rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest')

VALIDATION_DIR = "images/test/"
validation_datagen = ImageDataGenerator(rescale = 1./255)

train_generator = training_datagen.flow_from_directory(
TRAINING_DIR,
target_size=(112,150),
class_mode='categorical',
batch_size=50
)

validation_generator = validation_datagen.flow_from_directory(
VALIDATION_DIR,
target_size=(112,150),
class_mode='categorical',
batch_size=50
)

model = tf.keras.models.Sequential([
  # Note the input shape is the desired size of the image 150x150 with 3 bytes color
  # This is the first convolution
  tf.keras.layers.Conv2D(64, (3,3), activation='relu', input_shape=(112, 150, 3)),
  tf.keras.layers.MaxPooling2D(2, 2),
  # The second convolution
  tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  # The third convolution
  tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  # The fourth convolution
  tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  # Flatten the results to feed into a DNN
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dropout(0.5),
  # 512 neuron hidden layer
  tf.keras.layers.Dense(512, activation='relu'),
  tf.keras.layers.Dense(3, activation='softmax')
])


model.summary()

model.compile(loss = 'categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

history = model.fit(train_generator, epochs=40, steps_per_epoch=20, validation_data = validation_generator, verbose = 1, validation_steps=3)

model.save("model/squat.h5")
