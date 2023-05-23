import numpy as np
import cv2
import json

liste = []
liste_json = []
coherent = ""
val = None 
count = 0

img = cv2.imread('fichiers/scan.jpg')

height_image, width_image = img.shape[:2]

with open('fichiers/coordinates.json') as user_file:

  data = json.load(user_file)

  for i in data['information']:
    
    type = i['Types']
    valeur_x1 = i['coordinates']['x1']
    valeur_y1 = i['coordinates']['y1']
    valeur_x2 = i['coordinates']['x2']
    valeur_y2 = i['coordinates']['y2']
    id_Ex = i['id']['id_Ex']
    id_Q = i['id']['id_Q']
    id_A = i['id']['id_A']
    
    x1 = int(width_image * (valeur_x1 / 210))
    y1 = int(height_image * (valeur_y1 / 294))
    x2 = int(width_image * (valeur_x2 / 210))
    y2 = int(height_image * (valeur_y2 / 294))

    bloc = img[y1:y2, x1:x2]
    bloc_gris = cv2.cvtColor(bloc, cv2.COLOR_BGR2GRAY)
    bloc_hist = cv2.calcHist([bloc], [0], None, [256], [0, 256])

    if mediane(bloc_hist) > 142:  
      #bloc n'est pas noirci 
      val = 0
      liste.append(0)
    else:
      #bloc est noirci
      val = 1
      liste.append(1)

if type == '1parmiN' or type == 'mtf' :
  for elem in liste : 
      if elem == 1:
        count = count + 1
  if count > 1:
      coherent = 'incoherent'
  else: 
      coherent = 'coherent'

