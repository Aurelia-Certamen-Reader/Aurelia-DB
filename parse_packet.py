import os
import re
import json

"""
Object Structures:
Round:
{
    "series": str,
    "division": str,
    "year": int,
    "number": int | "final",
    "questions": []
}

Question:
{
    "number": int,
    "question": str,
    "answer": str
    "boni": [
        {
            "question": str,
            "answer": str
        }
    ]
}
"""

def getTossupMarker(file : str) -> str:
    if tossupMatch := re.findall(r"^(?:Tossup|TU|Toss-up|Toss up)\s?#?\d{1,2}:?\s?", file, re.MULTILINE | re.IGNORECASE): # := is for assignment within expressions
        return re.sub(r"\d{1,2}", r"(?P<number>\\d{1,2})", re.escape(tossupMatch[0])) # replace the number with a capturing group called "number"
    elif tossupMatch:= re.findall(r"^\d{1,2}(?:\.|:)\s", file, re.MULTILINE):
        return re.sub(r"\d{1,2}", r"(?P<number>\\d{1,2})", re.escape(tossupMatch[0]))
    else:
        print(f"ERROR: Could not determine tossup format ({file})")
        return ""

def getBonusMarker(file : str) -> str:
    if bonusMatch := re.findall(r"^(?:Bonus 1|B1|Bonus).?:?\s?", file, re.MULTILINE | re.IGNORECASE):
        return re.sub(r"\d", r"\\d", bonusMatch[0])
    else:
        print(f"WARNING: Could not find boni ({file})")
        return ""

def isAnswer(text : str):
    """
    Returns the answer string if it is an answer, returns None if it doesn't fit the answer format
    """
    if match := re.match(r"ans(?:wer)?:\s?", text, re.IGNORECASE):
        return text[len(match.group()):]
    if match := re.match(r"^[^a-zāēīōū]+$", text):
        return text
    return None

def updateText(dictionary : dict, key : str, text : str, lineNumber : int) -> None:
    if key not in dictionary or not dictionary[key]:
        dictionary[key] = text
        return
    else:
        dictionary[key] += "\n" + text

def parseText(fileName: str, inDir: str, outDir: str) -> None:
    # Setup
    file = open(os.path.join(inDir, fileName), encoding="utf-8").read()
    bestTossupMarker = getTossupMarker(file)
    if not bestTossupMarker:
        return
    bestBonusMarker = getBonusMarker(file)
    file = file.splitlines()
    round = {}
    round["series"], round["division"], round["year"] = fileName[:-4].split("_")
    round["year"] = int(round["year"])  
    round["number"] = None
    round["questions"] = []
    state = None
    
    # Parse, line by line
    for i in range(len(file)):
        line = file[i]
        if not line: # if page break
            state = None
            continue
        elif match := re.match(bestTossupMarker, line): # if it's a tossup
            state = "tossup"
            round["questions"].append({})
            question = round["questions"][-1]
            question["number"] = int(match.group("number"))
            question["question"] = line[len(match.group()):]
            question["answer"] = None
            question["boni"] = []
            continue
        elif bestBonusMarker and round["questions"] and (match := re.match(bestBonusMarker, line)):
            state = "bonus"
            round["questions"][-1]["boni"].append({"question": line[len(match.group()):], "answer":None})
            continue
        elif round["questions"] and (match := isAnswer(line)):
            question = round["questions"][-1]
            if question["boni"]:
                state = "bonusAnswer"
                updateText(question["boni"][-1], "answer", match, i)
            else:
                state = "tossupAnswer"
                updateText(question, "answer", match, i)
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
                    continue # It's a header, but doesn't contain the round number; will need to change if there's a packet where the question text is split across two pages

                if not round["number"]: # If the round currently doesn't have a number, update it
                    round["number"] = roundNum
                elif round["number"]!= roundNum: # If the round number is different from what currently exists, write the current round to a file and reset the round object
                    oldNum = round["number"]
                    with open(os.path.join(outDir, fileName[:-4] + "_" + ("final" if oldNum == "final" else "r"+str(oldNum)) + ".json"), "w", encoding="utf-8") as outfile:
                        outfile.write(json.dumps(round, indent=4))
                    round["questions"] = []
                    round["number"] = roundNum
                continue
            if state == "tossupAnswer":
                round["questions"][-1]["answer"] += "\n" + line
                continue
            if state == "bonusAnswer":
                round["questions"][-1]["boni"][-1]["answer"] += "\n" + line
                continue
            if i < len(file) - 1: 
                nextLine = file[i+1]
                if not (nextLine) or re.match(bestTossupMarker, nextLine) or (bestBonusMarker and re.match(bestBonusMarker, nextLine)): # if the next line is the start of a new question
                    if state == "tossup":
                        round["questions"][-1]["answer"] = line
                        continue
                    if state == "bonus":
                        round["questions"][-1]["boni"][-1]["answer"] = line
                        continue
            if state == "tossup": # NOT an else if; if there is a next line but it's not the start of a new question, then current line probably isn't an answer
                round["questions"][-1]["question"] += "\n" + line
                continue
            if state == "bonus":
                round["questions"][-1]["boni"][-1]["question"] += "\n" + line
                continue

    # Wrapping up
    with open(os.path.join(outDir, f"{fileName[:-4]}_{"final" if round["number"]=="final" else ("r"+str(round["number"]))}.json"), "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(round, indent=4))