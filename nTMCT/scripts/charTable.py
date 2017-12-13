# Uses Python 2

import csv
import sys
import json
from more_itertools import peekable
from collections import defaultdict

json_data = []
word_count = 0
NORMALIZE_COUNT = 100000
PRONOUNS = set(['he', 'she'])
FEMALE_REFS = set(['she', 'miss', 'mrs.'])
MALE_REFS = set(['he', 'mr.'])


# Function to get the normalized mention count
def normalizedCount(rawCount):
    global word_count
    global NORMALIZE_COUNT
    return float(rawCount * NORMALIZE_COUNT) / word_count

# Function to get predicted gender from BookNLP json file
def get_gender(id):
    global json_data
    for x in json_data["characters"]:
        if (str(x["id"]) == id):
            if (x["g"] == 0):
                return "?"
            elif (x["g"] == 1):
                return "F"
            elif (x["g"] == 2):
                return "M"
            else:
                return "Gender Error!"
    return "Character not found Error!"

def id_pronoun(word):
    global FEMALE_REFS
    global MALE_REFS

    word = word.lower()
    if word in FEMALE_REFS:
# 'she' or word == 'miss' or word == 'mrs.':
        return 'F'
    elif word in MALE_REFS:
#== 'he' or word == 'mr.':
        return 'M'
    else:
        return '?'


def create_char_table(outDir, text):
    alias = ""
    names = {}
    mentions = {}
    final_output = defaultdict(list)
    prRefs = defaultdict(list)
    gender_confidence = {}

    global word_count
    global json_data
    global PRONOUNS

    in_file = outDir + "/" + text + "/bookNLP/BookNLP.csv"
    md_file = outDir + "/" + text + "/bookNLP/metadata.csv"
    json_file = outDir + "/" + text + "/bookNLP/BookNLP.book"
    out_file = outDir + "/" + text + "/character_count.csv"

    print("---- Creating character table for: " + text + " ----")

    # Parse JSON file:
    with open(json_file) as data_file:
        json_data = json.load(data_file)

    # Get the total word count from the metadata.csv file
    with open(md_file, 'rb') as f:
        reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            if (row[0] == "Total Words"):
                word_count = int(row[1])
        if (word_count == 0):
            print("There was an error reading the metadata.csv file!")
            sys.exit()


    # Create the character.csv file!
    with open(in_file, 'rb') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

        peekableReader = peekable(reader)
        next(peekableReader, None)
        for row in peekableReader:
            if (row[14] != '-1'):
                charID = row[14]
                alias = alias + row[7]

                prRefs.setdefault(charID, [0,0])
                pronounID = id_pronoun(row[9])
                if (pronounID == 'F'):
                    prRefs[charID][0] += 1
                elif (pronounID == 'M'):
                    prRefs[charID][1] += 1

                if (charID == peekableReader.peek()[14]) and (peekableReader.peek()[9] not in PRONOUNS) and (row[9] not in PRONOUNS):
                    alias = alias + " "
                    continue

                mentions.setdefault(charID, 0)
                mentions[charID] += 1
                #Use first non-pronoun reference as primary name
                names.setdefault(charID, alias)
                alias = ""

        for d in (names, mentions):
            for key, value in d.iteritems():
                final_output[key].append(value)

        for key, value in prRefs.iteritems():
            if value[0] > value[1]:
                gender_confidence[key] = float(value[0]) / float(value[0] + value[1])
            elif value[1] > value[0]:
                gender_confidence[key] = float(value[1]) / float(value[0] + value[1])
            else:
                gender_confidence[key] = "0.5"

        for entry in final_output:
            final_output[entry].append(normalizedCount(final_output[entry][1]))
            final_output[entry].append(get_gender(entry))
            final_output[entry].append(gender_confidence[entry])

        with open(out_file, 'wb') as g:
            writer = csv.writer(g, delimiter='\t')
            w = csv.writer(g)

            # Add a header
            w.writerow(["Character ID", "Character Name", "Mentions", "Mentions / 100K Words", "Gender", "Confidence"])

            # Output values to csv
            for key, value in final_output.items():
                w.writerow([key] + value)

    print("---- Character table created. ----")
