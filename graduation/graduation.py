import csv
import random
import statistics
import numpy as np
import matplotlib.pyplot as plt
import json

################### Constant ###################

SUCCESS_QUESTION_STATS_COLUMNS = [
    "question_id",
    "exam_id",
    "number_of_good_answer",
    "number_of_wrong_answer",
]
SUCCESS_EXERCISE_STATS_COLUMNS = [
    "exercise_id",
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
    question_id with its answers and the score for each answer
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
    the exam to generate a tuple with the grades per student and the number of bad
    and good answers per question for each exercise.
    PARAMETERS
    -------
    parsingresult : dictionary
        dictionary following the schema defined for parsing result
    filename : string
        path of the file of the exam
    """
    # preparation of dictionaries for results
    counters = {}
    grades = {}
    scores = {}
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
    # processing
    for i in parsingResult:
        student = i["studentId"]
        score = 0
        scores[student] = {}
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
                            scoreAnswers = min
                        score += scoreAnswers
                        scores[student][id] = scoreAnswers

        grades[student] = score
    return (grades, counters, scores)


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


def successByExercise(success):
    """Function creating the dictionary of success for each exercise
    PARAMETERS
    -------
    success: dictionary
        dictionary representing the success for each question of each exercise
        2nd object of the tuple result of the function answerReading"""
    res = {}
    for ex in success:
        res[ex] = {}
        res[ex]["gAnswers"] = 0
        res[ex]["bAnswers"] = 0
        for q in success[ex]:
            res[ex]["gAnswers"] += success[ex][q]["gAnswers"]
            res[ex]["bAnswers"] += success[ex][q]["bAnswers"]
    return res


def successByConcept(success, exam):
    res = {}
    init = []
    for ex in success:
        for q in success[ex]:
            for i in exam["exercises"]:
                for j in i["questions"]:
                    if q == j["idQ"]:
                        c = j["qConcept"]
                        # iniate the dictionary
                        if not (c in init):
                            init.append(c)
                            res[c] = {}
                            res[c]["gAnswers"] = 0
                            res[c]["bAnswers"] = 0
                        res[c]["gAnswers"] += success[ex][q]["gAnswers"]
                        res[c]["bAnswers"] += success[ex][q]["bAnswers"]
    return res


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
    # ax.plot(median, median, label="Median")
    print(median)
    # ax.plot(marks, variance, label="Variance", color="red")
    ax.set_ylabel("Number of grades")
    ax.set_title("Bar chart by grades")
    ax.legend(title="Grades")
    plt.show()


def graphSuccessConcept(dict, exam):
    dict = successByConcept(dict, exam)
    concepts = dict.keys()
    counts = {
        "Good answers": np.array([dict[i]["gAnswers"] for i in dict.keys()]),
        "Wrong answers": np.array([dict[i]["bAnswers"] for i in dict.keys()]),
    }
    fig, ax = plt.subplots()
    bottom = np.zeros(3)
    for boolean, count in counts.items():
        p = ax.bar(concepts, count, 0.5, label=boolean, bottom=bottom)
        bottom += count
    ax.set_title("Success by concept")
    ax.legend(loc="upper right")
    plt.show()
    # TODO Work with percentages


################### CSV generator ###################


def listToString(list):
    res = ""
    for i in range(len(list) - 1):
        res += str(list[i]) + ","
    res += str(list[len(list) - 1]) + "\n"
    return res


def write_list_graduation(dict, exam_id):
    """Function generating a csv file of the grades per questions for every student
    IN : dictionary of the score per questions for each student id
    OUT : None
    SIDE EFFECT : creatin and/or writing a csv file of the score per questions for each student id
    """
    with open("./graduation/listgrades.csv", "w", newline="") as f:
        f.write(listToString(LISTGRADES_COLUMNS))
        writer = csv.DictWriter(f, fieldnames=LISTGRADES_COLUMNS)
        for i in dict:
            writer.writerow(
                {
                    LISTGRADES_COLUMNS[0]: i,
                    LISTGRADES_COLUMNS[1]: exam_id,
                    LISTGRADES_COLUMNS[2]: dict[i],
                }
            )


def write_success_question(dict, exam_id):
    with open("./graduation/successquestion.csv", "w", newline="") as f:
        f.write(listToString(SUCCESS_QUESTION_STATS_COLUMNS))
        writer = csv.DictWriter(f, fieldnames=SUCCESS_QUESTION_STATS_COLUMNS)
        for ex in dict:
            for q in dict[ex]:
                writer.writerow(
                    {
                        SUCCESS_QUESTION_STATS_COLUMNS[0]: q,
                        SUCCESS_QUESTION_STATS_COLUMNS[1]: exam_id,
                        SUCCESS_QUESTION_STATS_COLUMNS[2]: dict[ex][q]["gAnswers"],
                        SUCCESS_QUESTION_STATS_COLUMNS[3]: dict[ex][q]["bAnswers"],
                    }
                )


def write_success_exercise(dict, exam_id):
    dict = successByExercise(dict)
    with open("./graduation/successexercise.csv", "w", newline="") as f:
        f.write(listToString(SUCCESS_EXERCISE_STATS_COLUMNS))
        writer = csv.DictWriter(f, fieldnames=SUCCESS_EXERCISE_STATS_COLUMNS)
        for ex in dict:
            writer.writerow(
                {
                    SUCCESS_EXERCISE_STATS_COLUMNS[0]: ex,
                    SUCCESS_EXERCISE_STATS_COLUMNS[1]: exam_id,
                    SUCCESS_EXERCISE_STATS_COLUMNS[2]: dict[ex]["gAnswers"],
                    SUCCESS_EXERCISE_STATS_COLUMNS[3]: dict[ex]["bAnswers"],
                }
            )


def write_success_concept(dict, exam):
    dict = successByConcept(dict, exam)
    fields = ["Concept", "GoodAnswers", "BadAnswers"]
    with open("./graduation/successconcept.csv", "w", newline="") as f:
        f.write(listToString(fields))
        writer = csv.DictWriter(f, fieldnames=fields)
        for c in dict:
            writer.writerow(
                {
                    fields[0]: c,
                    fields[1]: dict[c]["gAnswers"],
                    fields[2]: dict[c]["bAnswers"],
                }
            )


################### Producing testing data ###################
exam_json = "./utils/exemple.json"
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

result = answerReading(readJSON("./graduation/res_parsing_test.json"), exam_json)
write_list_graduation(result[0], exam["examId"])
write_success_question(result[1], exam["examId"])
write_success_exercise(result[1], exam["examId"])
write_success_concept(result[1], exam)
bar_chart_by_grades(result[0], 20)
graphSuccessConcept(result[1], exam)
