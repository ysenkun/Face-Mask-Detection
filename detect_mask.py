from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os
import sys
import pprint
sys.path.remove('/Users/sen/Documents/research/facenet/src')
sys.path.remove('/opt/anaconda3/envs/facenet_mask/lib/python37.zip')
sys.path.remove('/opt/anaconda3/envs/facenet_mask/lib/python3.7')
sys.path.remove('/opt/anaconda3/envs/facenet_mask/lib/python3.7/lib-dynload')
sys.path.remove('/opt/anaconda3/envs/facenet_mask/lib/python3.7/site-packages')
sys.path.remove('/Users/sen/Documents/research/mask_detect/Face-Mask-Detection')
sys.path.append('/Users/sen/Documents/research/mask_detect/Face-Mask-Detection')
sys.path.append('/opt/anaconda3/envs/mask_test/lib/python39.zip')
sys.path.append('/opt/anaconda3/envs/mask_test/lib/python3.9')
sys.path.append('/opt/anaconda3/envs/mask_test/lib/python3.9/lib-dynload')
sys.path.append('/opt/anaconda3/envs/mask_test/lib/python3.9/site-packages')
pprint.pprint(sys.path)

def mask_image(img):
    # construct the argument parser and parse the arguments
    #ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--image", required=True,
    #     help="path to input image")
    # ap.add_argument("-f", "--face", type=str,
    #     default="face_detector",
    #     help="path to face detector model directory")
    # ap.add_argument("-m", "--model", type=str,
    #     default="mask_detector.model",
    #     help="path to trained face mask detector model")
    # ap.add_argument("-c", "--confidence", type=float, default=0.5,
    #     help="minimum probability to filter weak detections")
    #args = vars(ap.parse_args())
    # load our serialized face detector model from disk
    print("[INFO] loading face detector model...")
    prototxtPath = "/Users/sen/Documents/research/mask_detect/Face-Mask-Detection/face_detector/deploy.prototxt"
    weightsPath = "/Users/sen/Documents/research/mask_detect/Face-Mask-Detection/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
    net = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model from disk
    print("[INFO] loading face mask detector model...")
    model = load_model("/Users/sen/Documents/research/mask_detect/Face-Mask-Detection/mask_detector.model")
    print(5555555)
    
    # load the input image from disk, clone it, and grab the image spatial
    # dimensions
    #image = cv2.imread(args["image"])
    image = img
    #print(type(image),image)
    orig = image.copy()
    (h, w) = image.shape[:2]

    # construct a blob from the image
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
	(104.0, 177.0, 123.0))
    
    # pass the blob through the network and obtain the face detections
    print("[INFO] computing face detections...")
    net.setInput(blob)
    detections = net.forward()
    
    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the detection
        confidence = detections[0, 0, i, 2]
	# filter out weak detections by ensuring the confidence is
	# greater than the minimum confidence
        if confidence > args["confidence"]:
            # compute the (x, y)-coordinates of the bounding box for
            # the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            return box
            (startX, startY, endX, endY) = box.astype("int")
            # ensure the bounding boxes fall within the dimensions of
            # the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
            
	    # extract the face ROI, convert it from BGR to RGB channel
	    # ordering, resize it to 224x224, and preprocess it
            face = image[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)
            face = np.expand_dims(face, axis=0)
            # pass the face through the model to determine if the face
            # has a mask or not
            (mask, withoutMask) = model.predict(face)[0]

            # determine the class label and color we'll use to draw
            # the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            # include the probability in the label
            #label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box rectangle on the output
            # frame
            # cv2.putText(image, label, (startX, startY - 10),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            # cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
            # print(startX,startY,endX,endY)

    # show the output image
    #cv2.imshow("Output", image)
    #cv2.waitKey(0)
	
if __name__ == "__main__":
    mask_image()
