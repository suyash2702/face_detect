# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 15:45:45 2018

@author: suyash.a
"""

#!/usr/bin/python
from __future__ import division
import dlib
from imutils import face_utils
import cv2
import numpy as np
from scipy.spatial import distance as dist

def resize(img, width=None, height=None, interpolation=cv2.INTER_AREA):
    global ratio
    w, h = img.shape
    if width is None and height is None:
        return img
    elif width is None:
        ratio = height / h
        width = int(w * ratio)
        resized = cv2.resize(img, (height, width), interpolation)
        return resized
    else:
        ratio = width / w
        height = int(h * ratio)
        resized = cv2.resize(img, (height, width), interpolation)
        return resized
######
def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(36,48):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords
def eye_aspect_ratio_left(eye):
    A = dist.euclidean(eye[1], eye[5])
	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    print (A,C)
	# compute the eye aspect ratio
    #ear = (A + B) / (2.0 * C)
    ear1 = A/C
    return ear1

def eye_aspect_ratio_right(eye):
    B = dist.euclidean(eye[2], eye[4]) 
	 #compute the euclidean distance between the horizontal
	 #eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    print (B,C)
	 #compute the eye aspect ratio
    #ear = (A + B) / (2.0 * C)
    ear2 = B/C
    return ear2

camera = cv2.VideoCapture(0)

predictor_path = 'shape_predictor_68_face_landmarks.dat_2'

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
total_blinks = 0
total_winks = 0
m1 = 0
m2 = 0
while True:
    ret, frame = camera.read()
    if ret == False:
        print('Failed to capture frame from camera. Check camera index in cv2.VideoCapture(0) \n')
        break

    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_resized = resize(frame_grey, width=240)

# Ask the detector to find the bounding boxes of each face. The 1 in the
# second argument indicates that we should upsample the image 1 time. This
# will make everything bigger and allow us to detect more faces.
    dets = detector(frame_resized, 1)
    
    if len(dets) > 0:
        for k, d in enumerate(dets):
            shape = predictor(frame_resized, d)
            shape = shape_to_np(shape)
            leftEye= shape[lStart:lEnd]
            rightEye= shape[rStart:rEnd]
            ear1 = eye_aspect_ratio_left(leftEye)
            ear2 = eye_aspect_ratio_right(rightEye)
            ear = (ear1 + ear2) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)	       
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            if ear1>.21 and ear2>.21:
                print (ear1,ear2)
                m1=1
                m2=1
                print ('o')
                cv2.putText(frame, "Eyes Open ", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                if ear1>.21 or ear2>.21:
                    total_winks+=1
                    print ('wink')
                    m1=0
                    m2=0
                    cv2.putText(frame, "wink" ,(250, 30),cv2.FONT_HERSHEY_SIMPLEX, 1.7, (0, 0, 0), 4)
                elif  ear1<=.21 and ear2<=.21:
                    total_blinks+=1
                    print ('blink')
                    m1=0
                    m2=0
                    cv2.putText(frame, "blink" ,(250, 30),cv2.FONT_HERSHEY_SIMPLEX, 1.7, (0, 0, 0), 4)
                print (ear1,ear2)
                cv2.putText(frame, "Eyes closed".format(total_blinks+total_winks), (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            
            cv2.putText(frame, "Total Blinks: {}".format(total_blinks), (410, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(frame, "Total Winks: {}".format(total_winks), (410, 70),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            for (x, y) in shape:
                cv2.circle(frame, (int(x/ratio), int(y/ratio)), 3, (255, 255, 255), -1)
    cv2.imshow("image", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        camera.release()
        break