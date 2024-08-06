import pdf_to_text
import parse_packet
import os

INPUT_DIRECTORY = "packets\\input"
OUTPUT_DIRECTORY_1 = "packets\\extracted"
OUTPUT_DIRECTORY_2 = "packets\\parsed"

files = os.listdir(INPUT_DIRECTORY)

for file in files:
    pdf_to_text.extractText(file, INPUT_DIRECTORY, OUTPUT_DIRECTORY_1)
    parse_packet.parseText(file[:-4]+".txt", OUTPUT_DIRECTORY_1, OUTPUT_DIRECTORY_2)