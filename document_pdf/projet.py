#!/usr/bin/env python3
import fpdf
import json

#variables globales
nb_page = 0
border = 0
rect_size = 5
x_offset = 2
y_offset = 1
exam = None
pdf = None
liste_coordonnees = []

def setAnswerMCQ_1pN(a, type_q, id_Ex, id_Q, id_A):
	"""ecrit les reponses à une question"""
	x, y = pdf.get_x(), pdf.get_y()
	pdf.rect(x+x_offset, y+y_offset, rect_size, rect_size)
	liste_coordonnees.append((type_q, x+x_offset, y+y_offset, pdf.get_x()+x_offset+rect_size, pdf.get_y()+y_offset+rect_size, id_Ex, id_Q, id_A))
	pdf.set_xy(x+10, y)
	answerLabel = a['answerLabel']	
	pdf.cell(0, 7, answerLabel, border, 1, align='L')

def setMedia(media):
	"""permet d'afficher les medias en lien avec une question"""
	#pdf.cell(0, 10, media['mediaTitle'], 1, 1, align='L')
	pdf.image(media['path'], w=media['width'], h=media['height'])

def setMCQ_1pN(q, type_q, id_Ex, id_Q):
	qStatement = q['qStatement']
	if ((q["numberOfAnswers"]+1) * 8 + pdf.get_y() > 287):
		pdf.add_page()
	pdf.multi_cell(0, 8, qStatement, border, align='L')
	if 'media' in q:
		if ((q["numberOfAnswers"]+1) * 8 + pdf.get_y() + q['media']['Media'][0]['height'] > 287):
			pdf.add_page()
			setMedia(q['media']['Media'][0])
	#accéder aux réponses
	answers = q['answers']['Answer']
	for a in answers :
		id_A = a['answerId']
		setAnswerMCQ_1pN(a, type_q, id_Ex, id_Q, id_A)

def setMultipleTF(q, id_Ex, id_Q):
	qStatement = q['qStatement']
	pdf.cell(0, 10, qStatement, border, 1, align='L')
	pdf.cell(8, 4, 'T', border, 0, align='C')
	pdf.cell(8, 4, 'F', border, 1, align='C')
	for mtf in q["mtfs"]["Mtfs"]:
		id_A = mtf['answerId']
		x, y = pdf.get_x(), pdf.get_y()
		pdf.rect(x+x_offset, y+y_offset, rect_size, rect_size)
		pdf.rect(x + x_offset + rect_size +2, y+y_offset, rect_size, rect_size)
		liste_coordonnees.append(("mtf", x+x_offset, y+y_offset, pdf.get_x()+x_offset+rect_size, pdf.get_y()+y_offset+rect_size, id_Ex, id_Q, id_A))
		liste_coordonnees.append(("mtf", x+x_offset + rect_size +2, y+y_offset, pdf.get_x()+x_offset+rect_size + rect_size +2, pdf.get_y()+y_offset+rect_size, id_Ex, id_Q, id_A))
		pdf.set_x(x+x_offset+2*rect_size+5)
		pdf.cell(0, 7, mtf['answerLabel']	, border, 1, align='L')
		
def setQuestion(q, id_Ex, id_Q):
	"""ecrit la question avec ses medias"""
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

def setMarker():
	"""met les repère pour le parsing des question"""
	pdf.image("./marqueur.jpg", 5, 5, 5)
	pdf.image("./marqueur.jpg", 200, 5, 5)
	pdf.image("./marqueur.jpg", 5, 287, 5)
	pdf.image("./marqueur.jpg", 200, 287, 5)
	liste_coordonnees.append(("Marker", 5, 5, 10, 10, "m"+str(0),0,0))
	liste_coordonnees.append(("Marker", 5, 5, 10, 10, "m"+str(1),0,0))
	liste_coordonnees.append(("Marker", 5, 5, 10, 10, "m"+str(2),0,0))
	liste_coordonnees.append(("Marker", 5, 5, 10, 10, "m"+str(3),0,0))
	
def set_nb_page(nb_page):
	x = pdf.get_x()
	nb_page_binaire = bin(nb_page)
	nb_page_binaire = nb_page_binaire[2:]
	pdf.set_x(150)
	pdf.text(pdf.get_x()-20, 9, "Page : " + str(nb_page))
	for i in range(4):
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
	

def setBody(copyID, lenCopyId):
	"""rempli le corps de la copie"""
	global nb_page
	#accéder aux exercices
	exercises = exam['exercises']['Exercise']
	for ex in exercises:
		setEx(ex)
		id_Ex = ex['exerciseId']
		#accéder aux questions
		questions = ex['questions']['Question']
		for q in questions :
			y = pdf.get_y()
			id_Q = q['idQ']
			setQuestion(q, id_Ex, id_Q)
			if y > pdf.get_y(): #permet de mettre les marqueurs sur chaque page
				nb_page = nb_page+1
				setCopyID(copyID, lenCopyId)
				setMarker()
				

def setstudentId(studentId):
	"""permettra de mettre les cases nécessaire au numéro étudiant"""
	pdf.set_xy(100, pdf.get_y())
	for i in range(10):
		pdf.cell(5, 5, str(i), border, 0, align='C')
		pdf.set_xy(pdf.get_x() + 5, pdf.get_y())
	pdf.set_xy(100, pdf.get_y()+5)
	for i in range(studentId):
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
	#diff entre examid et copyid  ?? examId = exam.get('examId')
	message = exam.get('message')
	exercises = exam.get('exercises')
	studentId = exam.get('lenStudentId')
	copyID = exam.get('copyId')
	lenCopyId = exam.get('lenCopyId')
	
	#ecrire ces propriétés dans le pdf
	writtingHead(title, message, copyID, studentId, lenCopyId)

def loadExam() : 
	"""stock dans exam le JSON"""
	global exam
	with open('exemple.json') as mon_fichier:
		exam = json.load(mon_fichier)

# recupérer le json (plus tard récupérer le nom en ligne de commande)
loadExam()
#initialiser l'en-tête de la copie
setHead()
#initialiser marqueur
setMarker()
#remplir le reste de la copie
setBody(exam.get('copyId'), exam.get('lenCopyId'))
#renvoyer le pdf
pdf.output(name='./output-file.pdf')


#créer JSON coordonnées et remplir
with open("coordinates.json", "w") as f:
	f.write("[\n")
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
	f.write("\n]\n")

