import os
import re
import json

OUTPUT_DIRECTORY = "output"
TEST_FILE = "texas_advanced_2010.txt"

NEW_ROUND = {
    "series": None,
    "division": None,
    "year": None,
    "number": None,
    "questions": []
}

NEW_QUESTION = {
    "question": "",
    "answer": "",
    "boni": []
}

TOSSUP_MARKERS = [
    r"^(?:Tossup|TU|Toss-up|Toss\sup)\s?#?\d+:?\s?"
]

# def isRoundHeader(text : str, seriesName : str, ) -> bool:
#     if bool(re.search(r'(?i)certamen', text)) and :

#     return False

def isAnswer(text : str):
    """
    Returns the answer string if it is an answer, returns None if it doesn't fit the answer format
    """
    if match := re.match(r"ans(?:wer)?:\s?", text, re.IGNORECASE):
        return text[len(match.group()):]
    if match := re.match(r"^[a-zāēīōū]+$", text):
        return text
    return None

rounds = []

file = open(os.path.join(OUTPUT_DIRECTORY, TEST_FILE), encoding="utf-8").read()
bestTossupMarker = None
bestBonusMarker = None

if tossupMatch := re.findall(r"^(?:Tossup|TU|Toss-up|Toss up)\s?#?\d{1,2}:?\s?", file, re.MULTILINE | re.IGNORECASE): # := is for assignment within expressions
    bestTossupMarker = re.sub(r"\d{1,2}", r"(?P<number>\\d{1,2})", tossupMatch[0]) # replace the number with a capturing group called "number"
elif re.findall(r"^\d{1,2}\.\s", file, re.MULTILINE):
    bestTossupMarker = r"\d{1,2}\s"
else:
    print("ERROR: Could not determine tossup format")
    quit()

if bonusMatch := re.findall(r"^(?:Bonus 1|B1|Bonus).?:?", file, re.MULTILINE | re.IGNORECASE):
    bestBonusMarker = re.sub(r"\d", r"\\d", bonusMatch[0])
else:
    print("WARNING: Could not find boni")

file = file.splitlines()

round = NEW_ROUND
round["series"], round["division"], round["year"] = TEST_FILE[:-4].split("_")
round["year"] = int(round["year"])  

state = question = bonus = None

for i in range(len(file)):
    line = file[i]
    if not line: # if page break
        state = question = bonus = None
        if bonus:
            question["boni"].append(bonus)
            bonus = None
        if question:
            round["questions"].append(question)
            question = None
        continue
    elif match := re.match(bestTossupMarker, line): # if it's a tossup
        state = "tossup"
        if bonus:
            question["boni"].append(bonus)
            bonus = None
        if question: # if there was already a question, add it to the list
            round["questions"].append(question)
        question = NEW_QUESTION
        question["question"] = line[len(match.group()):]
        question["number"] = match.group("number")
        question["boni"] = []
        continue
    elif bestBonusMarker and (match := re.match(bestBonusMarker, line)):
        if bonus:
            question["boni"].append(bonus)  
        state = "bonus"
        bonus = {"question": match.group()}
        continue
    elif match := isAnswer(line):
        if state == "tossup":
            state = "tossupAnswer"
            question["answer"] = match
        if state == "bonus": 
            state = "bonusAnswer"
            bonus["answer"] = match
        continue
    ### Handling unspecified text:
    else:
        if state == None or state == "header":
            if bonus:
                question["boni"].append(bonus)
                bonus = None
            if question:
                round["questions"].append(question)
                question = None
            state = "header"
            # header handling
            continue
        if state == "tossupAnswer":
            question["answer"] += " " + line
            continue
        if state == "bonusAnswer":
            bonus["answer"] += line
            continue
        if i < len(file) - 1:
            nextLine = file[i+1]
            if not (nextLine) or re.match(bestTossupMarker, nextLine) or (bestBonusMarker and re.match(bestBonusMarker, nextLine)):
                if state == "tossup":
                    question["answer"] = line
                    # round["questions"].append(question)
                    # question = None
                    continue
                if state == "bonus":
                    bonus["answer"] = line
                    continue
        else:
            if state == "tossup":
                question["question"] += line
                continue
            if state == "bonus":
                bonus["question"] += line
                continue

if bonus:
    question["boni"].append(bonus)
if question:
    round["questions"].append(question)
rounds.append(round)

for round in rounds:
    with open(os.path.join(OUTPUT_DIRECTORY, TEST_FILE[:-4] + ".json"), "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(round, indent=4))