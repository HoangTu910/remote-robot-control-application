import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

offset = 20
imgSize = 300
counter = 0
folder = "images/Turn Right"

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)*255

        try:
            imgCrop = img[y-offset:y+h+offset, x-offset:x+w+offset]
            try:
                aspect_ratio = h/w
                if aspect_ratio > 1:
                    prev_aspect = h/w
                    new_witdh = math.ceil(imgSize / prev_aspect)
                    imgResize = cv2.resize(imgCrop, (new_witdh, imgSize))
                    y_remain = math.ceil((imgWhite.shape[1] - imgResize.shape[1])/2)
                    imgWhite[0:imgResize.shape[0], y_remain:imgResize.shape[1]+y_remain] = imgResize
                else:
                    prev_aspect = h / w
                    new_height = math.ceil(imgSize * prev_aspect)
                    imgResize = cv2.resize(imgCrop, (imgSize, new_height))
                    x_remain = math.ceil((imgWhite.shape[0] - imgResize.shape[0]) / 2)
                    imgWhite[x_remain:imgResize.shape[0]+x_remain, 0:imgResize.shape[1]] = imgResize
                cv2.imshow("imgWhite", imgWhite)
                cv2.imshow("ImageCrop", imgCrop)
            except:
                print("Out of imgWhite")
        except:
            print("Out of imgCrop")
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    if key == ord("s"):
        counter += 1
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', imgWhite)
        print(counter)
