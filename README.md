# Aurelia DB
A collection of scripts that manage the parsing and uploading of certamen packets.

## How to use
Run `runner.py` to extract & parse files, then `runner_upload.py` to upload them to MongoDB. Questions and rounds that were not successfully uploaded can be found in `packets\failed`. Fix the issues in them (remove `error` fields), put them back in `packets\parsed`, and rerun `runner_upload.py`. 

## The scripts
`runner.py`: Extracts text from PDF files and parses text files into JSON rounds. Uses `pdf_to_text.py` and `parse_packet.py`.

`runner_upload.py`: Attempts to upload JSON rounds to the MongoDB server. Uses `upload_round.py`.

## The `packets` directory
```
packets
├── input: input PDFs
├── extracted: TXT files produced from extraction; to be parsed
├── parsed: JSON files produced from parsing; to be uploaded
├── success: questions that were successfully uploaded
├── failed: rounds/questions that were not uploaded correctly
└── used
    ├── pdfs: PDFs where the text has been extracted
    └── txts: TXTs where the text has been parsed
```