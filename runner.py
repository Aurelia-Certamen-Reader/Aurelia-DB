"""Simple script to extract and parse PDF packets."""

import pdf_to_text
import parse_packet
import os

INPUT_PDFS = "packets\\input"
EXTRACTED_TEXT = "packets\\extracted"
PARSED_JSON = "packets\\parsed"

# extract text
files = os.listdir(INPUT_PDFS)
for file in files:
    pdf_to_text.extractText(file, INPUT_PDFS, EXTRACTED_TEXT)
    os.rename(os.path.join(INPUT_PDFS, file), os.path.join("packets\\used\\pdfs", file)) # move to used pdfs

# parse packets
files = os.listdir(EXTRACTED_TEXT)
for file in files:
    parse_packet.parseText(file, EXTRACTED_TEXT, PARSED_JSON)
    os.rename(os.path.join(EXTRACTED_TEXT, file), os.path.join("packets\\used\\txts", file)) # move to used txts