import csv
import random
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

################### Constant ###################

SUCCESS_STATS_COLUMNS = [
    "question_id",
    "exam_id",
    "number_of_good_answer",
    "number_of_wrong_answer",
]
LISTGRADES_COLUMNS = ["student_id", "exam_id", "mark"]

################### Reading JSON ###################


def readJSON(filename):
    with open(filename, "r") as f:
        exam = json.load(f)
    return exam


def questionsList(filename):
    """Function reading an exam following the JSON Schema to catch the
    question_id with its answers
    IN : string of the filename
    OUT : list of question id"""
    with open(filename, "r") as f:
        questions = {}
        exam = json.load(f)
        for i in exam["exercises"]:
            for j in i["questions"]:
                id = j["idQ"]
                answer = {}
                for k in j["answers"]:
                    answer[(k["answerId"])] = k["score"]
                questions[id] = answer
    return questions


def minScoreQuestion(exam, id):
    for ex in exam["exercises"]:
        for q in ex["questions"]:
            if q["idQ"] == id:
                return q["minScoreQuestion"]


################### Reading Parsing ###################


def answerReading(parsingResult, filename):
    """Function reading the answers found in the parsing result, and matching with
    the exam to generate the exam

    PARAMETERS
    -------
    parsingresult : dictionary
        ???? #TODO Explain
    filename : string
        path of the file of the exam
    IN : dictionary of the parsingResult, ?????
    OUT : Tuple of grades per student and proportions of good and bad answers per question
    """
    # preparation of dictionaries for results
    counters = {}
    grades = {}
    questions = questionsList(filename)
    exam = readJSON(filename)
    for i in parsingResult:
        grades[i["studentId"]] = 0
    for j in exam["exercises"]:
        counters[j["exerciseId"]] = {}
        for k in j["questions"]:
            counters[j["exerciseId"]][k["idQ"]] = {}
            counters[j["exerciseId"]][k["idQ"]]["gAnswers"] = 0
            counters[j["exerciseId"]][k["idQ"]]["bAnswers"] = 0
    for i in parsingResult:
        student = i["studentId"]
        score = 0
        for id in i["questions"]:
            for ex in counters:
                for q in counters[ex]:
                    if q == id:
                        scoreAnswers = 0
                        min = minScoreQuestion(exam, id)
                        answers = i["questions"][id]
                        for a in answers:
                            if a == "NULL":
                                break
                            else:
                                scoreAnswer = questions[id][a]
                                scoreAnswers += scoreAnswer
                                if scoreAnswer <= 0:
                                    counters[ex][id]["bAnswers"] += 1
                                else:
                                    counters[ex][id]["gAnswers"] += 1
                        if scoreAnswers < min:
                            score += min
                        else:
                            score += scoreAnswers
        grades[student] = score
    return (grades, counters)


################### Graduation ###################


def gradesv1(parsing_result, filename):
    """Function creating a dictionnary with the score per question for each student
    by reading the parsing_result and match the information with the exam. Example for testing,
    not the final version we will use.
    IN : parsing_result (data format to define), exam (dictionnary or JSON file ?)
    OUT : dictionnary with the score per question for each student"""
    exam = readJSON(filename)
    grades = answerReading(parsing_result, filename)[0]
    counter = {}
    for i in range(int(exam["maxScore"] + 1)):
        counter[i] = 0
    for i in grades:
        mark = int(grades[i])
        counter[mark] += 1
    return counter


################### Statistics ###################


################### Chart generator ###################


def bar_chart_by_grades(grades, max_score):
    # representation by percentages might not be adapted for each type of question
    # add a parameter for the type of question ?
    marks = range(int(max_score) + 1)
    grades_only = []
    counter = [0 for i in range(int(max_score) + 1)]
    for i in grades:
        mark = int(grades[i])
        grades_only.append(mark)
        counter[mark] += 1
    median = statistics.median(grades_only)
    variance = [statistics.variance(grades_only) for i in range(int(max_score) + 1)]
    fig, ax = plt.subplots()
    ax.bar(marks, counter)
    ax.plot(median, median, label="Median")
    print(median)
    ax.plot(marks, variance, label="Variance", color="red")
    ax.set_ylabel("Number of grades")
    ax.set_title("Bar chart by grades")
    ax.legend(title="Grades")
    plt.show()


################### CSV generator ###################


def write_graduation(dict):
    """Function generating a csv file of the grades per questions for every student
    IN : dictionary of the score per questions for each student id
    OUT : None
    SIDE EFFECT : creatin and/or writing a csv file of the score per questions for each student id
    """

    # dict -> {student_id:{question_id:mark, question_id:mark}}
    fields = ["Student"] + list(dict[0])
    with open("graduation.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fields)
        for i in dict:
            writer.writerow({"Student": i} + dict[i])


################### Producing testing data ###################
exam_json = "./examtest.json"
exam = readJSON(exam_json)
# current_exam = questionsList(exam_json)

# res_parsing = []
# students = list(range(22202000, 22202011))
# for i in range(len(students)):
#     student = str(students[i])
#     copy = {"examId": exam["examId"],
#             "studentId": students[i], "questions": {}}
#     for j in current_exam.keys():
#         max = len(current_exam[j].keys())
#         n = random.randint(0, max-1)
#         answers = list(current_exam[j].keys())
#         copy["questions"][j] = [answers[n]]
#     res_parsing.append(copy)

# with open("./res_parsing_test.json", 'w') as f:
#     f.write(json.dumps(res_parsing))
# print(res_parsing)


############ Tests ###############

# structure test

# possible_parsing_result = {"22202055": {}, "22202056": {}, "22202057": {
# }, "22202058": {}, "22202059": {}, "22202060": {}, "22202061": {}}
# for i in possible_parsing_result:
#     for j in range(1, 11):
#         mark = round(random.uniform(0, 2.2), 1)
#         possible_parsing_result[i][j] = mark

# test_grades = gradesv1(possible_parsing_result)
# print(possible_parsing_result)
# print(test_grades)
# bar_chart_by_grades(test_grades, 20)

result = answerReading(readJSON("./res_parsing_test.json"), exam_json)
print(result[0])
bar_chart_by_grades(result[0], exam["maxScore"])
