"""Script that uploads rounds."""

import os
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import upload_round

uri = os.getenv("MONGO_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
rounds = client["Testing"]["Rounds"]
questions = client["Testing"]["Questions"]

files = os.listdir("packets\\parsed")
for file in files:
    print("Uploading", file)
    round = open(os.path.join("packets\\parsed", file), "r", encoding="utf-8")
    round = json.load(round)
    try:
        result = upload_round.uploadRound(round, rounds, questions)
        if(len(result["success"])!=0): # handle successful qs
            round["questions"] = result["success"]
            outfile = open(os.path.join("packets\\success", file), "w", encoding="utf-8")
            outfile.write(json.dumps(round, indent=4, ensure_ascii=False))
        if(len(result["fail"])!=0): # handle invalid qs
            round["questions"] = result["fail"]
            outfile = open(os.path.join("packets\\failed", file), "w", encoding="utf-8")
            outfile.write(json.dumps(round, indent=4, ensure_ascii=False))
    except Exception as e:
        print(e)
    os.remove(os.path.join("packets\\parsed", file)) # delete it