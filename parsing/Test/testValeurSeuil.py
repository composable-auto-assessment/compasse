import cv2
import numpy as np

img = cv2.imread('blocs.jpg')

def median(hist):
  histCum = np.cumsum(hist)
  mediane = np.where(histCum >= histCum[255] / 2)[0][0]
  return mediane


bloc1 = img[866:888, 266:297] 
bloc1_gris = cv2.cvtColor(bloc1, cv2.COLOR_BGR2GRAY)
bloc1_hist = cv2.calcHist([bloc1_gris], [0], None, [256], [0, 256])

bloc2 = img[691:706, 476:500] 
bloc2_gris = cv2.cvtColor(bloc2, cv2.COLOR_BGR2GRAY)
bloc2_hist = cv2.calcHist([bloc2_gris], [0], None, [256], [0, 256])

print("La médiane du bloc legerement noirci est de : ", median(bloc1_hist))
print("La médiane du bloc bien noirci est de : ", median(bloc2_hist))

cv2.imshow('bloc legerement noirci', bloc1) 
cv2.imshow('bloc bien noirci', bloc2)
cv2.waitKey(0)


