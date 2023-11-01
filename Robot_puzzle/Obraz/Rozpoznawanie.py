import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np


def model():
    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)
    labels_path = '/home/pi/Desktop/Robot_puzzle/Obraz/model/labels.txt'
    labelsfile = open(labels_path, 'r')

    # initialize classes and read in lines until there are no more
    classes = []
    line = labelsfile.readline()
    while line:
        # retrieve just class name and append to classes
        classes.append(line.split(' ', 1)[1].rstrip())
        line = labelsfile.readline()
    labelsfile.close()

    # Load the model
    model = tensorflow.keras.models.load_model('/home/pi/Desktop/Robot_puzzle/Obraz/model/keras_model.h5')
    return model, classes

def start(model,classes):
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(9, 224, 224, 3), dtype=np.float32)
    k= 0
    for i in range(1,4):
        for j in range(1,4):
            image = Image.open('ROI_0'+str(i)+'_0'+str(j)+'.png')

            #resize the image to a 224x224 with the same strategy as in TM2:
            #resizing the image to be at least 224x224 and then cropping from the center
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.ANTIALIAS)

            #turn the image into a numpy array
            image_array = np.asarray(image)

            # display the resized image
            #image.show()

            # Normalize the image
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

            # Load the image into the array
            data[k] = normalized_image_array
            k += 1

    # run the inference
    predictions = model.predict(data)
    # confidence threshold is 90%.
    conf_threshold = 70
    confidence = []
    threshold_class = {}
    puzzle_cyfry = ""

    for j in range(9):
        confidence = []
        # for each one of the classes
        for i in range(0, len(classes)):
            # scale prediction confidence to % and apppend to 1-D list
            confidence.append(int(predictions[j][i]*100))

            # if above confidence threshold, send to queue
            if confidence[i] > conf_threshold:
                threshold_class[j]= int(classes[i])
                puzzle_cyfry += classes[i]

    print("threshold class" ,threshold_class)
    print(puzzle_cyfry)
    return puzzle_cyfry
