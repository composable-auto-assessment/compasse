from matplotlib import pyplot as plt 
import cv2
import numpy as np

img = cv2.imread('blocsTestBleu.png')

def median(hist):
  histCum = np.cumsum(hist)
  mediane = np.where(histCum >= histCum[255] / 2)[0][0]
  return mediane

blocBleu = img[974:994, 441:489] 
blocBleu_gris = cv2.cvtColor(blocBleu, cv2.COLOR_BGR2GRAY)
blocBleu_hist = cv2.calcHist([blocBleu_gris], [0], None, [256], [0, 256])

print("La médiane du bloc coloré en bleu est de : ", median(blocBleu_hist))

cv2.imshow('bloc bleu', blocBleu)
cv2.imshow('bloc bleu mis en niveau de gris', blocBleu_gris)
cv2.waitKey(0)

