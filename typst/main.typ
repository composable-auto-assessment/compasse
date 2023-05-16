/* Calibrage */
#place(top+left, dx : -60pt, dy : -60pt, square(size: 10pt, fill : black))
#place(bottom+right, dx : 60pt, dy : 60pt, square(size: 10pt, fill : black))

/* Logo */


/* Une fonction pour tout
- type_q : type de la question (multiple true false, 1 parm N...)
- type_a : type d'affichage : afficher les réponses en sautant une ligne = "saut"
                              à la suite = "suite"
- q : question
*/

#let affichage_question(type_q,type_a, q)=[
  /* type de question */
  #if type_q == "MCQ"{
    [_plusieurs réponses peuvent être justes_]
  }
  else if type_q == "1parmiN"{
    [_une seule réponse est juste_]
  }

  /* type d'affichage */
  #if type_a == "suite"{
     columns( q.numberOfAnswers, gutter : -200pt)[
        #let nOA = q.numberOfAnswers
        #align(center)[
          /* Pour chaque réponse */
          #for a in q.answers.Answer {
            block()[#v(5pt)#a.answerLabel
            #align(center)[#box(square(size : 10pt))]
            ]
            if nOA > 1 {
              colbreak()
            }
            nOA=nOA - 1
        }
        #v(20pt)//espacement après exo
        ]]
  }
  else{
    for a in q.answers.Answer [
      #box(square(size : 10pt)) #h(8pt) #a.answerLabel
      #v(2pt)
    ]
     v(10pt)//espacement après exo
  }

]

#let forecast(exam) =[
  #columns(2, gutter: 2.5cm)[#rect(width: 7cm, height: 2cm, inset: 11pt)[#set text( size: 13pt)
  Nom : 
  
  Prenom : ]
  #colbreak()
  #rect(width: 7cm, height: 2cm, inset : 11pt)[#set text(size : 13pt)
  Numéro Étudiant :]]
  #v(20pt)
  #set heading(numbering:"1.") //Numérotation
  // Espace identifiant étudiant
  #underline[*#align(center, text(size : 15pt, exam.title))*] //Titre
  #place(top+right, dx : 50pt, dy : -50pt, [#rect[#exam.examId]]) //Identifiant
  /* Parcourir chaque exercice */
  #for ex in exam.exercises.Exercise {
    block()
      [#align(center)[#rect[= #upper[#text(size : 13pt, "Exercice")]]]//Titre de l'exercice
      #align(center)[#ex.eSText] //Énoncé de l'exercice
      #v(15pt)
      /* Parcourir chaque question */
      #for q in ex.questions.Question {
          [== #q.qStatement]
          affichage_question(q.questionType, "saut", q)
      }
      ] 
  }
]

#forecast(json("examtest.json"))