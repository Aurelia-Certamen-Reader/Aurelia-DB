"""Module that provides methods for validating and uploading packets."""

import os
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection

def validateRound(round):
    """Validate a round. A round is considered invalid if:
    - it is missing metadata
    - it doesn't have questions
    - the division isn't recognized
    - the questions are out of order (or some numbers are skipped)
    """

    if not (round["series"] and round["division"] and round["year"] and round["number"]):
        print("Missing metadata")
        return False
    if not round["questions"]:
        print("Missing questions")
        return False
    if round["division"] not in ['novice', 'intermediate', 'advanced', 'elite']:
        print("Invalid division")
        return False
    currentNum = round["questions"][0]["number"] # might start at 0, might start at 1
    for i in range(1, len(round["questions"])):
        if round["questions"][i]["number"] != currentNum+1:
            print("Questions out of order")
            return False
        currentNum+=1
    return True
    

def validateQuestion(question):
    """Validate a question. A round is considered invalid if:
    - it is question/answer text
    - boni are missing question/answer text

    Returns True if the question is valid.
    Returns False if it is not, and adds a field "error" to the question with a description of the issue.
    """

    if not question["question"]:
        question["error"] = "Missing question"
        return False
    if not question["answer"]:
        question["error"] = "Missing answer"
        return False
    for bonus in question["boni"]:
        if not (bonus["question"] and bonus["answer"]):
            question["error"] = "Incomplete boni"
            return False
    return True
    

def uploadRound(round: dict, rounds_collection: Collection, questions_collection: Collection):
    """Upload a round to a MongoDB cluster. Return failed and successful question uploads.

    Keyword arguments:
    - round: round to upload
    - rounds_collection: Mongo Collection for round objects
    - questions_collection: Mongo Collection for question objects
    """

    # if round is invalid, return without uploading
    if not validateRound(round):
        return {"success": [], "fail": round["questions"]}
    
    roundID = None
    roundExists = False
    # insert the round if it doesn't exist in the DB
    if foundRound:= rounds_collection.find_one({"series":round["series"], "division":round["division"], "year":round["year"], "number":round["number"]}):
        roundID = foundRound["_id"]
        roundExists = True
    else:
        roundID = rounds_collection.insert_one({"series":round["series"], "division":round["division"], "year":round["year"], "number":round["number"]}).inserted_id

    # upload questions
    invalidQuestions = []
    validQuestions = []
    for question in round["questions"]:
        if not validateQuestion(question): # if the question is invalid, don't upload
            invalidQuestions.append(question)
            continue
        if roundExists and (foundQuestion := questions_collection.find_one({"round":roundID, "number":question["number"]})): # if the question is already in the DB
            if (question["question"] == foundQuestion["question"]) and (question["answer"]==foundQuestion["answer"]) and (question["boni"]==foundQuestion["boni"]): # duplicate of an existing question
                temp = {"_id":str(foundQuestion["_id"])}
                temp.update(question)
                validQuestions.append(temp)
                continue
            else: # matches round and number, but fields don't match
                question["error"] = "Conflicts with existing question"
                invalidQuestions.append(question)
                continue
        # if it doesn't match an existing question, add it to the DB
        temp = {"round":roundID}
        temp.update(question)
        temp = {"_id": str(questions_collection.insert_one(temp).inserted_id)}
        validQuestions.append(question)

    return {"success":validQuestions, "fail":invalidQuestions}