import numpy as np
import cv2

# calling classifiers for face and eye
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

img = cv2.imread('example.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


faces = face_cascade.detectMultiScale(gray, 1.3, 5)
for (x,y,w,h) in faces:
    print x,y,w,h
#img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2) <-- know if function will perform action in place or anew
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,255),2)
    roi_gray = gray[y:y+h, x:x+w]
    print 'img is ', img
    roi_color = img[y:y+h, x:x+w]

    # eyes = eye_cascade.detectMultiScale(roi_gray)
    # for (ex,ey,ew,eh) in eyes:
    #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)


# shows forementioned image under header "img"
# wait for key to kills all opened HighGUI windows
cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows('img', img)

