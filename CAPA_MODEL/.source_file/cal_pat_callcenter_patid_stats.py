import pandas as pd
import numpy as np

import nndw as nn

iotype = 'db'


def splitText(data):
    
    res = data.split(";")
    
    return res
	

def aggData(rawData):
    questionData = rawData.copy()
    patID = questionData.iloc[0].patient_id
    questions = []
    
    for tempList in questionData["question_list"]:
        for item in tempList:
            if item != "":
                questions.append(item.strip())
    
    patQuestDf = pd.DataFrame(questions, columns=["customer_question"])
    patQuestDf.insert(0, "patient_id", patID)
    
    return patQuestDf


def sepQuestions(raw):
    allData = raw.copy()
    resDf = []
    patList = allData.patient_id.unique()
    allData["question_list"] = allData.customer_question.apply(splitText)

    for pat in patList:
        subData = allData[allData.patient_id==pat][["patient_id", "question_list"]]
        res = aggData(subData)
        resDf.append(res)

    finalDf = pd.concat(resDf, ignore_index=True)
    
    return finalDf


def main():
    raw = nn.Dataframefactory("pat_call_center",iotype = iotype)
    mapping = nn.Dataframefactory("pat_call_mapping",iotype = iotype)
    
    print("Begin aggregating patient questions")
    patQuesDf = sepQuestions(raw)
    print("Patient questions prepared")
    
    print("Begin calculating")
    quesMerge = pd.merge(patQuesDf, mapping, how="left", left_on="customer_question", right_on="question")
    output = quesMerge[["patient_id", "customer_question", "question_category", "question_sub_category", "product_type"]]
    print("Finished calculating")
    
    nn.write_table(output,'pat_call_center_stats', iotype = iotype)
	# pat_call_center_stats structure: five columns - patient_id, customer_question, question_category, question_sub_category, product_type
    
    return (1)   



