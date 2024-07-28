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

state = None

for i in range(len(file)):
    line = file[i]
    if not line: # if page break
        state = None
        continue
    elif match := re.match(bestTossupMarker, line): # if it's a tossup
        state = "tossup"
        round["questions"].append({})
        question = round["questions"][-1]
        question["question"] = line[len(match.group()):]
        question["number"] = match.group("number")
        question["boni"] = []
        continue
    elif bestBonusMarker and (match := re.match(bestBonusMarker, line)):
        state = "bonus"
        round["questions"][-1]["boni"].append({"question": match.group()})
        continue
    elif match := isAnswer(line):
        if state == "tossup":
            state = "tossupAnswer"
            round["questions"][-1]["answer"] = match
        if state == "bonus": 
            state = "bonusAnswer"
            round["questions"][-1]["boni"][-1]["answer"] = match
        continue
    ### Handling unspecified text:
    else:
        if state == None: # Probably a header
            # header handling
            roundNum = None
            if match := re.search(r"Round (?P<num>\d)", line, re.IGNORECASE):
                roundNum = int(match.group("num"))
            elif match := re.search(r"Round (?P<num>One|Two|Three|Four|Five|Six|Seven|Eight|Nine)", line, re.IGNORECASE):
                roundNum = {"one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eight":8, "nine":9}[match.group("num").lower()] 
            elif re.search(r"\bround\b", line, re.IGNORECASE) and (match := re.search(r"finals?\b", line, re.IGNORECASE)):
                roundNum = "final"
            else:
                continue

            if not round["number"]:
                round["number"] = roundNum
            elif round["number"]!= roundNum:
                oldNum = round["number"]
                with open(os.path.join(OUTPUT_DIRECTORY, TEST_FILE[:-4] + "_" + ("final" if oldNum == "final" else "r"+str(oldNum)) + ".json"), "w", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(round, indent=4))
                round["questions"] = []
                round["number"] = roundNum
            continue
        if state == "tossupAnswer":
            round["questions"][-1]["answer"] += " " + line
            continue
        if state == "bonusAnswer":
            round["questions"][-1]["boni"][-1]["answer"] += line
            continue
        if i < len(file) - 1:
            nextLine = file[i+1]
            if not (nextLine) or re.match(bestTossupMarker, nextLine) or (bestBonusMarker and re.match(bestBonusMarker, nextLine)):
                if state == "tossup":
                    round["questions"][-1]["answer"] = line
                    # round["questions"].append(question)
                    # question = None
                    continue
                if state == "bonus":
                    round["questions"][-1]["boni"][-1]["answer"] = line
                    continue
        else:
            if state == "tossup":
                round["questions"][-1]["question"] += line
                continue
            if state == "bonus":
                round["questions"][-1]["boni"][-1]["question"] += line
                continue


with open(os.path.join(OUTPUT_DIRECTORY, f"{TEST_FILE[:-4]}_{"final" if round["number"]=="final" else ("r"+str(round["number"]))}.json"), "w", encoding="utf-8") as outfile:
    outfile.write(json.dumps(round, indent=4))