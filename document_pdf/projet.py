#!/usr/bin/env python3
import fpdf
import json

#variables globales
border = 0
rect_size = 5
x_offset = 2
y_offset = 1
exam = None
pdf = None
liste_coordonnees = []

def setAnswerMCQ_1pN(a, type_q):
	"""ecrit les reponses à une question"""
	x, y = pdf.get_x(), pdf.get_y()
	pdf.rect(x+x_offset, y+y_offset, rect_size, rect_size)
	liste_coordonnees.append((type_q, ((x+x_offset,y+y_offset), (pdf.get_x()+x_offset+rect_size, pdf.get_y()+y_offset+rect_size)), a['answerId']))
	pdf.set_xy(x+10, y)
	answerLabel = a['answerLabel']	
	pdf.cell(0, 7, answerLabel, border, 1, align='L')

def setMedia(media):
	"""permet d'afficher les medias en lien avec une question"""
	#pdf.cell(0, 10, media['mediaTitle'], 1, 1, align='L')
	pdf.image(media['path'], w=media['width'], h=media['height'])

def setMCQ_1pN(q, type_q):
	qStatement = q['qStatement']
	if ((q["numberOfAnswers"]+1) * 8 + pdf.get_y() > 287):
		pdf.add_page()
	pdf.multi_cell(0, 8, qStatement, border, align='L')
	if 'media' in q:
		setMedia(q['media']['Media'][0])
	#accéder aux réponses
	answers = q['answers']['Answer']
	for a in answers :
		setAnswerMCQ_1pN(a, type_q)

def setMultipleTF(q):
	#TODO rajouter coordonées dans liste 
	qStatement = q['qStatement']
	pdf.cell(0, 10, qStatement, border, 1, align='L')
	pdf.cell(8, 4, 'T', border, 0, align='C')
	pdf.cell(8, 4, 'F', border, 1, align='C')
	#rajouter un for avec toute les questions du multipleTF dedans, genre on parcours la q
	for mtf in q["mtfs"]["Mtfs"]:
		x, y = pdf.get_x(), pdf.get_y()
		pdf.rect(x+x_offset, y+y_offset, rect_size, rect_size)
		pdf.rect(x + x_offset + rect_size +2, y+y_offset, rect_size, rect_size)
		liste_coordonnees.append(("mtf", ((x+x_offset,y+y_offset), (pdf.get_x()+x_offset+rect_size, pdf.get_y()+y_offset+rect_size)), mtf['answerId']))
		liste_coordonnees.append(("mtf", ((x+x_offset + rect_size +2,y+y_offset), (pdf.get_x()+x_offset+rect_size + rect_size +2, pdf.get_y()+y_offset+rect_size)), mtf['answerId']))
		pdf.set_x(x+x_offset+2*rect_size+5)
		pdf.cell(0, 7, mtf['answerLabel']	, border, 1, align='L')
		
	

def setQuestion(q):
	"""ecrit la question avec ses medias"""
	type_q = q['questionType']
	#version trop vieille de python pour case
	if type_q=='MCQ' or type_q=='1parmiN':
		setMCQ_1pN(q, type_q)
	elif type_q=='multipleTF' :
		setMultipleTF(q)
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
	pdf.image("./marqueur.png", 0, 0, 10)
	pdf.image("./marqueur.png", 200, 0, 10)
	pdf.image("./marqueur.png", 0, 287, 10)
	pdf.image("./marqueur.png", 200, 287, 10)

def setCopyID(copyID, lenCopyId):
	"""permet de mettre le code de la copie sous forme de case"""
	for i in range(lenCopyId):
		pdf.rect(pdf.get_x(), rect_size, rect_size, rect_size, style='DF') if copyID[i]=="1" else pdf.rect(pdf.get_x(), rect_size, rect_size, rect_size, style='D')
		liste_coordonnees.append(("CopyId", ((pdf.get_x(), rect_size), (pdf.get_x()+rect_size, rect_size*2)), i))
		pdf.set_x(pdf.get_x()+rect_size)

def setBody(copyID, lenCopyId):
	"""rempli le corps de la copie"""
	#accéder aux exercices
	exercises = exam['exercises']['Exercise']
	for ex in exercises:
		setEx(ex)
		#accéder aux questions
		questions = ex['questions']['Question']
		for q in questions :
			y = pdf.get_y()
			setQuestion(q)
			if y > pdf.get_y(): #permet de mettre les marqueurs sur chaque page
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
			liste_coordonnees.append(("StudendId", ((pdf.get_x(), pdf.get_y()), (pdf.get_x()+5, pdf.get_y()+5)), j))
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
	for types, coordinates, identity in liste_coordonnees:
		donnee = {"Types": types, "Coordinates": coordinates, "id": identity}
		json.dump(donnee, f)
		f.write('\n')


"""
TODO : 
	- clean code
	- revérifier les coordonnées
	- rajouter coordonnées MTF et marker
	- rajouter un numéro de page 
	
"""


