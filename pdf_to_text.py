import pymupdf
import re
import os

# TEST_FILE = "C:\\Users\\saffr\\Downloads\\texas_advanced_2010.pdf"
TEST_FILE = "texas_advanced_2010.pdf"
INPUT_DIRECTORY = "input"
OUTPUT_DIRECTORY = "output"
MACRON_MISREPRESENTATIONS = {
    "Ā":["Ɩ"],
    "Ē":["Ɯ"],
    "Ī":["¦", "Ʈ"],
    "Ō":["ƿ", "Æ"],
    "Ū":["â", "ǋ"],
    "ā":["Ɨ"],
    "ē":["Ɲ"],
    "ī":["Ư"],
    "ō":["ǀ"],
    "ū":["ǌ"]
}
MACRONS = "ĀĒĪŌŪāēīōū"

PUNCTUATION_SUBSTITUTES = {
    "\"":["“", "”"],
    "'":["‘", "’"],
    "-":["–"],
    "...":["…"]
}
PUNCTUATION = r".?!,:;#\-—&='\"/()\[\]" 

UNKNOWN_CHARACTER_PATTERN = fr"(?a)[^\w\s{MACRONS}{PUNCTUATION}]" # (?a) means only ASCII matching (otherwise the weird characters will be counted as unicode letters)

def fixMacrons(text : str) -> str:
    for vowel, badChars in MACRON_MISREPRESENTATIONS.items():
        for badChar in badChars:
            text = text.replace(badChar, vowel)
    weirdChars = re.findall(UNKNOWN_CHARACTER_PATTERN, text)
    if len(weirdChars) > 0:
        print(f"{text} has unknown characters: {weirdChars}")
    return text

def standardizePunctuation(text : str) -> str:
    for punct, badChars in PUNCTUATION_SUBSTITUTES.items():
        for badChar in badChars:
            text = text.replace(badChar, punct)
    return text

def extractText(fileName: str, inDir: str, outDir: str) -> None:
    doc = pymupdf.open(os.path.join(inDir, fileName))
    outfile =  open(os.path.join(outDir, fileName[:-3]+"txt"), "w", encoding="utf-8")
    for page in doc:
        blocks = page.get_text("blocks") # type: ignore
        for block in blocks:
            block = fixMacrons(standardizePunctuation(block[4])).strip()
            block = re.sub(r"\s+", " ", block)
            if block!= "":
                outfile.write(block + "\n")
        outfile.write("\n")
    return

def printArr(arr : list[str]) -> str:
    out = "["
    for item in arr:
        out += f"\n    \'{item}\',"
    out+="\n]"
    return out

def parse(fileName:str ) -> None:
    return