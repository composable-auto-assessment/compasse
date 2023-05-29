import cv2
import numpy as np 
import json 
import sys

liste_json = []

def median(hist):
  histCum = np.cumsum(hist)
  mediane = np.where(histCum >= histCum[255] / 2)[0][0]
  return mediane

def formatArguments():
	if len(sys.argv) != 2:
		print("Format : nom_programme imageScannee.jpg/.png")
		sys.exit(1) 

formatArguments()
img = cv2.imread(sys.argv[1])

height_image, width_image = img.shape[:2]

with open('coordinates.json') as user_file:
  
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
    y1 = int(height_image * (valeur_y1 / 297))
    x2 = int(width_image * (valeur_x2 / 210))
    y2 = int(height_image * (valeur_y2 / 297))

    bloc = img[y1:y2, x1:x2]
    bloc_gris = cv2.cvtColor(bloc, cv2.COLOR_BGR2GRAY)
    bloc_hist = cv2.calcHist([bloc], [0], None, [256], [0, 256])

    if median(bloc_hist) <= 142:  
      #print(type,"la case est noircie")
      liste_json.append((type, id_Ex, id_Q, id_A))
    #else:
      #print(type,"la case n'est pas noircie")
      
with open("coordonneesSortie.json", "w") as f: 
  f.write("{\n\"Cases noircies\":[\n")
  for type, id_Ex, id_Q, id_A in liste_json:
    donnee = {
       "Type": type, 
        "id": 
          {"id_Ex": id_Ex, "id_Q": id_Q, "id_A": id_A}}
    json.dump(donnee, f) 
    f.write(",\n")   
  f.seek(f.tell() -2, 0)  
  f.truncate()  
  f.write("\n]\n}\n")  

