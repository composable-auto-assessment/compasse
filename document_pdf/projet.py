#!/usr/bin/env python3
import fpdf
import json
import sys

#variables globales
nb_page = 0
border = 0
rect_size = 5
x_offset = 2 #pour avoir un joli alignement des carrées
y_offset = 1
exam = None
pdf = None
liste_coordonnees = []

def setMarker():
	"""met les 4 repères pour le parsing des question"""
	pdf.image("./marqueur.jpg", 5, 5, 5)
	pdf.image("./marqueur.jpg", 200, 5, 5)
	pdf.image("./marqueur.jpg", 5, 287, 5)
	pdf.image("./marqueur.jpg", 200, 287, 5)
	liste_coordonnees.append(("Marker", 5, 5, 10, 10, "m"+str(0),0,0))
	liste_coordonnees.append(("Marker", 200, 5, 205, 10, "m"+str(1),0,0))
	liste_coordonnees.append(("Marker", 5, 287, 10, 292, "m"+str(2),0,0))
	liste_coordonnees.append(("Marker", 200, 287, 205, 292, "m"+str(3),0,0))
	
def set_nb_page(nb_page):
	"""ecrit le numéro de page et le code correspondant"""
	x = pdf.get_x()
	nb_page_binaire = bin(nb_page)
	nb_page_binaire = nb_page_binaire[2:]
	pdf.set_x(150)
	pdf.text(pdf.get_x()-20, 9, "Page : " + str(nb_page))
	for i in range(4): #ecrit le code en binaire et codé au maximum sur 4 case soit 16 pages
		pdf.rect(pdf.get_x(), rect_size, rect_size, rect_size, style='DF') if len(str(nb_page_binaire))>i and nb_page_binaire[i]=="1" else pdf.rect(pdf.get_x(), rect_size, rect_size, rect_size, style='D')
		liste_coordonnees.append(("Page_ID", pdf.get_x(), rect_size, pdf.get_x()+rect_size, rect_size*2, "p"+str(i), 0, 0))
		pdf.set_x(pdf.get_x()+rect_size)
	pdf.set_x(x)

def setCopyID(copyID, lenCopyId):
	"""permet de mettre le code de la copie sous forme de case"""
	pdf.set_x(pdf.get_x()+10)
	for i in range(lenCopyId):
		pdf.rect(pdf.get_x(), rect_size, rect_size, rect_size, style='DF') if copyID[i]=="1" else pdf.rect(pdf.get_x(), rect_size, rect_size, rect_size, style='D')
		liste_coordonnees.append(("CopyId", pdf.get_x(), rect_size, pdf.get_x()+rect_size, rect_size*2, "c"+str(i), 0, 0))
		pdf.set_x(pdf.get_x()+rect_size)
	set_nb_page(nb_page)

def setAnswerMCQ_1pN(a, type_q, id_Ex, id_Q, id_A):
	"""ecrit les reponses à une question de type 1 parmi N ou QCM"""
	x, y = pdf.get_x(), pdf.get_y()
	pdf.rect(x+x_offset, y+y_offset, rect_size, rect_size)
	liste_coordonnees.append((type_q, x+x_offset, y+y_offset, pdf.get_x()+x_offset+rect_size, pdf.get_y()+y_offset+rect_size, id_Ex, id_Q, id_A))
	pdf.set_xy(x+10, y) #se décaler pour que la réponse ne soit pas collé à la case
	answerLabel = a['answerLabel']	
	pdf.cell(0, 7, answerLabel, border, 1, align='L')

def setMedia(media):
	"""permet d'afficher le media en lien avec une question"""
	pdf.image(media['path'], w=media['width'], h=media['height'])

def setMCQ_1pN(q, type_q, id_Ex, id_Q):
	"""ecrit la question (et le media) pour le type 1 parmi N et QCM"""
	qStatement = q['qStatement']
	if ((q["numberOfAnswers"]+1) * 8 + pdf.get_y() > 287): #si on n'a pas toutes les réponses sur la même page on change de page
		pdf.add_page()
	pdf.multi_cell(0, 8, qStatement, border, align='L')
	if 'media' in q:
		if ((q["numberOfAnswers"]+1) * 8 + pdf.get_y() + q['media'][0]['height'] > 287): #on garde groupé l'image avec les réponses et donc change de page si besoin
			pdf.add_page()
		setMedia(q['media'][0])
	#accéder aux réponses
	answers = q['answers']
	for a in answers :
		id_A = a['answerId']
		setAnswerMCQ_1pN(a, type_q, id_Ex, id_Q, id_A)

def setMultipleTF(q, id_Ex, id_Q):
	"""ecrit les question et réponses pour le type multiple true false"""
	qStatement = q['qStatement']
	pdf.cell(0, 10, qStatement, border, 1, align='L')
	pdf.cell(8, 4, 'T', border, 0, align='C')
	pdf.cell(8, 4, 'F', border, 1, align='C')
	for mtf in q["answers"]: #pour chaque question du mtf
		id_A = mtf['answerId']
		x, y = pdf.get_x(), pdf.get_y()
		pdf.rect(x+x_offset, y+y_offset, rect_size, rect_size) #2 carrés, 1 pour True et un pour False
		pdf.rect(x + x_offset + rect_size +2, y+y_offset, rect_size, rect_size)
		liste_coordonnees.append(("mtf", x+x_offset, y+y_offset, pdf.get_x()+x_offset+rect_size, pdf.get_y()+y_offset+rect_size, id_Ex, id_Q, id_A))
		liste_coordonnees.append(("mtf", x+x_offset + rect_size +2, y+y_offset, pdf.get_x()+x_offset+rect_size + rect_size +2, pdf.get_y()+y_offset+rect_size, id_Ex, id_Q, id_A))
		pdf.set_x(x+x_offset+2*rect_size+5)
		pdf.cell(0, 7, mtf['answerLabel']	, border, 1, align='L')
		
def setQuestion(q, id_Ex, id_Q):
	"""ecrit les questions en fonction de leur type"""
	type_q = q['questionType']
	#version trop vieille de python pour case
	if type_q=='MCQ' or type_q=='1parmiN':
		setMCQ_1pN(q, type_q, id_Ex, id_Q)
	elif type_q=='multipleTF' :
		setMultipleTF(q, id_Ex, id_Q)
	elif type_q=='tableau' :
		print('Non réalisé')
	else : 
		print('Format de question non connu et donc non traité.') 

def setEx(ex):
	"""écrit les informations de début d'exercice"""
	title = ex['eSText']
	pdf.cell(0, 10, title, border, 1, align='C')

def setBody(copyID, lenCopyId):
	"""rempli le corps de la copie"""
	global nb_page
	#accéder aux exercices
	exercises = exam['exercises']
	for ex in exercises:
		setEx(ex)
		id_Ex = ex['exerciseId']
		#accéder aux questions
		questions = ex['questions']
		for q in questions :
			y = pdf.get_y()
			id_Q = q['idQ']
			new_page = setQuestion(q, id_Ex, id_Q)
			if nb_page+1 != pdf.page_no(): #permet de mettre les marqueurs sur chaque page
				x, y = pdf.get_x(), pdf.get_y()
				nb_page = nb_page+1
				setCopyID(copyID, lenCopyId)
				setMarker()
				pdf.set_xy(x, y)

def setstudentId(studentId):
	"""permettra de mettre les cases nécessaire au numéro étudiant"""
	pdf.set_xy(100, pdf.get_y())
	for i in range(10): #met le numéro pour la valeur
		pdf.cell(5, 5, str(i), border, 0, align='C')
		pdf.set_xy(pdf.get_x() + 5, pdf.get_y())
	pdf.set_xy(100, pdf.get_y()+5)
	for i in range(studentId): #boucles pour mettre les cases à cocher
		for j in range(10):
			pdf.rect(pdf.get_x(), pdf.get_y(), rect_size, rect_size, style='D')
			liste_coordonnees.append(("StudendId", pdf.get_x(), pdf.get_y(), pdf.get_x()+5, pdf.get_y()+5, "s"+str(j), 0, 0))
			pdf.set_x(pdf.get_x()+10)
		pdf.set_xy(100, pdf.get_y()+5)
	pdf.set_xy(10, pdf.get_y()+5)

def setName():
	"""permet d'avoir la case pour remplir manuellement le nom et prenom"""
	y = pdf.get_y()
	pdf.set_xy(10, 20)
	pdf.cell(80, 10, "Nom Prénom :", border="LTR", ln=1, align='L')
	pdf.cell(80,10, "..................................................................", border="LBR", ln=1, align='')
	pdf.set_xy(10, y)

def writtingHead(title, message, copyID, studentId, lenCopyId):
	"""écrit les informations de l'en-tête dans la copie"""
	global pdf
	pdf = fpdf.FPDF(orientation='portrait', format='A4') #rajouter la police modifiable
	pdf.set_font('Helvetica', '', 12)
	pdf.add_page()
	setCopyID(copyID, lenCopyId)
	setstudentId(studentId)
	setName()
	pdf.cell(0, 10, title, border, 1, align='C') #190 = largeur de la feuille, 0 rend pareil
	pdf.cell(190, 10, message, border, 1, align='C')


def setHead() :
	"""récupère et initialise l'en-tête de la copie"""
	# Accéder à certaines propriétés de l'objet exam
	title = exam.get('title')
	message = exam.get('message')
	exercises = exam.get('exercises')
	studentId = exam.get('lenStudentId')
	copyID = exam.get('copyId')
	lenCopyId = exam.get('lenCopyId')
	#ecrire ces propriétés dans le pdf
	writtingHead(title, message, copyID, studentId, lenCopyId)

def loadExam(nom_exam) : 
	"""stock dans exam le JSON"""
	global exam
	with open(nom_exam) as mon_fichier:
		exam = json.load(mon_fichier)

def test_arg():
	if len(sys.argv) != 3:
		print("convention : nom_programme nom_examen_a_traduire.json nom_fichier_sorti.pdf")
		sys.exit(1) 

test_arg()
# recupérer le json (plus tard récupérer le nom en ligne de commande)
loadExam(sys.argv[1])
#initialiser l'en-tête de la copie
setHead()
#initialiser marqueur
setMarker()
#remplir le reste de la copie
setBody(exam.get('copyId'), exam.get('lenCopyId'))
#renvoyer le pdf
pdf.output(name=sys.argv[2])


#créer JSON coordonnées et remplir
with open("coordinates.json", "w") as f:
	f.write("{\n\"information\":[\n")
	for types, x1, y1, x2, y2, id_Ex, id_Q, id_A in liste_coordonnees:
		donnee = {
			"Types": types, 
			"coordinates": 
				{"x1": x1, "y1": y1, "x2": x2, "y2": y2}, 
			"id": 
				{"id_Ex": id_Ex, "id_Q": id_Q, "id_A" :id_A}}
		json.dump(donnee, f)
		f.write(",\n")  # Ajoute une virgule et le retour ligne
	# Après la boucle, nous devons supprimer la dernière virgule pour obtenir un JSON valide
	f.seek(f.tell() - 2, 0)  # Place le curseur deux caractères avant la fin du fichier
	f.truncate()  # Supprime les caractères restants (la dernière virgule et le saut de ligne)
	f.write("\n]\n}\n")

