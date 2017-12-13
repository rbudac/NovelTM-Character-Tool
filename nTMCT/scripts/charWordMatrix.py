# Uses Python 2
# Step 3(?) extract related words.

import csv
import sys
import os
from collections import defaultdict

AGENT_ID_WORDS = set(['nsubj', 'nsubjpass'])
AGENT_FIND_WORDS = set(['cop', 'ccomp', 'xcomp', 'aux', 'auxpass', 'advmod',
                        'neg', 'advcl', 'dep', 'conj', 'dobj', 'pobj',
                        'iobj'])
PATIENT_ID_WORDS = set(['dobj', 'iobj', 'pobj'])
PATIENT_FIND_WORDS = set(['nsubj', 'cop', 'ccomp', 'xcomp', 'aux', 'auxpass',
                          'advmod', 'neg', 'advcl', 'dep', 'conj', 'dobj',
                          'pobj', 'iobj'])
PATIENT_STOP_WORDS = set(['nsubj', 'nsubjpass'])
POSS_ID_WORDS = set(['poss'])
POSS_FIND_WORDS = set(['dobj', 'pobj', 'nsubj', 'ccomp'])
POSS_IGNORE_WORDS = set(['punct', 'det'])
MOD_ID_WORDS_A = set(['nsubj', 'dobj', 'iobj', 'pobj'])
MOD_FIND_WORDS_A = set(['amod'])
MOD_STOP_WORDS_A = set(['cop', 'nsubj'])
MOD_ID_WORDS_B = set(['nsubj', 'nsubjpass'])
MOD_FIND_WORDS_B = set(['amod', 'advmod', 'ccomp'])
MOD_STOP_WORDS_B = set(['nsubj'])

final_output = defaultdict(dict)

def is_verb(item):
    if item[12] == 'null' and 'VB' in item[10]:
        return True
    else:
        return False

def agent(sentence, sentence_string):
    global AGENT_ID_WORDS
    global AGENT_FIND_WORDS
    global final_output


    char = '-1'
    assoc_words = []
    a_row = []
    list_to_return = []
    null_exists = False

    for item in sentence:
        if char != '-1':
            if item[12] in AGENT_FIND_WORDS:
                # Replace character mentions with their ID if possible.
                if item[14] != '-1':
                    assoc_words.append(item[14])
                    final_output[char].setdefault(item[14], 0)
                    final_output[char][item[14]] += 1
                else:
                    final_output[char].setdefault(item[9], 0)
                    final_output[char][item[9]] += 1
                    assoc_words.append(item[9])
            # Search forward for null verbs.
            # If found, associate and remove from sentence.
            if is_verb(item):
                null_exists = True
                final_output[char].setdefault(item[9], 0)
                final_output[char][item[9]] += 1
                assoc_words.append(item[9])
                sentence.remove(item)

        # If find a reason to terminate and start a new character:
        if item[12] in AGENT_ID_WORDS or (item[12] == 'cc' and null_exists):
            # CHANGE a_row to assoc_words to remove rows with no associated words
            if a_row != []:
                a_row.append(assoc_words)
                a_row.append(sentence_string)
                list_to_return.append(a_row)
            assoc_words = []
            a_row = []
            char = item[14]
            if char != '-1':
                a_row.append(item[14])

    # CHANGE a_row to assoc_words to remove rows with no associated words
    if a_row != []:
        a_row.append(assoc_words)
        a_row.append(sentence_string)
        list_to_return.append(a_row)

    # Search for null backward if no nulls were found while looking
    # forward.
    if not null_exists:
        char = '-1'
        assoc_words = []
        a_row = []
        for item in reversed(sentence):
            if char != '-1':
                if is_verb(item):
                    final_output[char].setdefault(item[9], 0)
                    final_output[char][item[9]] += 1
                    assoc_words.append(item[9])
                    break # MAYBE SHOULDN'T DO THIS...
            if item[12] in AGENT_ID_WORDS:
                # assoc_words = [] # Maybe SHOULD do this...
                a_row = []
                char = item[14]
                if char != '-1':
                    a_row.append(item[14])

        # CHANGE a_row to assoc_words to remove rows with no associated words
        if a_row != []:
            a_row.append(assoc_words)
            a_row.append(sentence_string)
            list_to_return.append(a_row)
    return list_to_return

# MAY NEED WORK? If we run into a new pobj while currently studying
# one, we include it for the current character but don't follow up on
# it afterward. (It gets ignored.)
# Not sure if this is a problem or not.
def patient(sentence, sentence_string):
    global final_output
    global PATIENT_ID_WORDS
    global PATIENT_FIND_WORDS
    global PATIENT_STOP_WORDS

    char = '-1'
    assoc_words = []
    a_row = []
    list_to_return = []
    null_exists = False

    # Scan through the sentence backwards
    for item in reversed(sentence):
        if char != '-1':
            if is_verb(item):
                null_exists = True
            if item[12] in PATIENT_FIND_WORDS or is_verb(item):
                if item[14] != '-1':
                    final_output[char].setdefault(item[14], 0)
                    final_output[char][item[14]] += 1
                    assoc_words.append(item[14])
                else:
                    final_output[char].setdefault(item[9], 0)
                    final_output[char][item[9]] += 1
                    assoc_words.append(item[9])


#            if item[12] in PATIENT_STOP_WORDS or (item[12] == 'cc' and null_exists):
            if item[13] in PATIENT_STOP_WORDS:
                if a_row != []:
                    a_row.append(assoc_words)
                    a_row.append(sentence_string)
                    list_to_return.append(a_row)
                assoc_words = []
                a_row = []
                char = '-1'
        if char == '-1' and item[14] != '-1' and item[12] in PATIENT_ID_WORDS:
                char = item[14]
                a_row.append(item[14])

    # CHANGE a_row to assoc_words to remove rows with no associated words
    if a_row != []:
        a_row.append(assoc_words)
        a_row.append(sentence_string)
        list_to_return.append(a_row)
    return list_to_return

def possession(sentence, sentence_string):
    global final_output
    global POSS_ID_WORDS
    global POSS_FIND_WORDS
    global POSS_IGNORE_WORDS

    char = '-1'
    assoc_words = []
    a_row = []
    list_to_return = []
    countdown = 2

    # Scan through the sentence
    for item in sentence:
        if char != '-1':
            if item[12] in POSS_FIND_WORDS:
                if item[14] != '-1':
                    final_output[char].setdefault(item[14], 0)
                    final_output[char][item[14]] += 1
                    assoc_words.append(item[14])
                else:
                    final_output[char].setdefault(item[9], 0)
                    final_output[char][item[9]] += 1
                    assoc_words.append(item[9])
            if item[12] not in POSS_IGNORE_WORDS and item[10] != 'NNP':
                countdown = countdown - 1
            if countdown == 0:
                if a_row != []:
                    a_row.append(assoc_words)
                    a_row.append(sentence_string)
                    list_to_return.append(a_row)
                assoc_words = []
                a_row = []		
                char = '-1'
        if char == '-1' and item[14] != '-1' and item[12] in POSS_ID_WORDS:
               char = item[14]
               a_row.append(item[14])
               countdown = 2

    # CHANGE a_row to assoc_words to remove rows with no associated words
    if a_row != []:
        a_row.append(assoc_words)
        a_row.append(sentence_string)
        list_to_return.append(a_row)
    return list_to_return

def modification(sentence, sentence_string):
    global final_output
    global MOD_ID_WORDS_A
    global MOD_FIND_WORDS_A
    global MOD_STOP_WORDS_A
    global MOD_ID_WORDS_B
    global MOD_FIND_WORDS_B
    global MOD_STOP_WORDS_B

    char = '-1'
    assoc_words = []
    a_row = []
    list_to_return = []
    check_for_cop = False

    # Scan through the sentence backward
    for item in reversed(sentence):
        if char != '-1':
            if item[12] in MOD_FIND_WORDS_A:
                if item[14] != '-1':
                    final_output[char].setdefault(item[14], 0)
                    final_output[char][item[14]] += 1
                    assoc_words.append(item[14])
                else:
                    final_output[char].setdefault(item[9], 0)
                    final_output[char][item[9]] += 1
                    assoc_words.append(item[9])
            if item[12] in MOD_STOP_WORDS_A or is_verb(item):
                if assoc_words != []:
                    a_row.append(assoc_words)
                    a_row.append(sentence_string)
                    list_to_return.append(a_row)
                assoc_words = []
                a_row = []
                char = '-1'
        if char == '-1' and item[14] != '-1' and item[12] in MOD_ID_WORDS_A:
                char = item[14]
                a_row.append(item[14])
                
    # CHANGE a_row to assoc_words to remove rows with no associated words
    if assoc_words != []:
        a_row.append(assoc_words)
        a_row.append(sentence_string)
        list_to_return.append(a_row)
    char = '-1'
    assoc_words = []
    a_row = []

    # Scan through the sentence if there's a cop after the nsubj
    for item in sentence:
        if check_for_cop:
            check_for_cop = False
            if item[12] != 'cop':
                assoc_words = []
                a_row = []
                char = '-1'
        if char != '-1':
            if item[12] in MOD_FIND_WORDS_B:
                if item[14] != '-1':
                    final_output[char].setdefault(item[14], 0)
                    final_output[char][item[14]] += 1
                    assoc_words.append(item[14])
                else:
                    final_output[char].setdefault(item[9], 0)
                    final_output[char][item[9]] += 1
                    assoc_words.append(item[9])
            if item[12] in MOD_STOP_WORDS_B or is_verb(item):
                if assoc_words != []:
                    a_row.append(assoc_words)
                    a_row.append(sentence_string)
                    list_to_return.append(a_row)
                assoc_words = []
                a_row = []
                char = '-1'
        if char == '-1' and item[14] != '-1' and item[12] in MOD_ID_WORDS_B:
            char = item[14]
            a_row.append(item[14])
            check_for_cop = True

    # CHANGE a_row to assoc_words to remove rows with no associated words
    if assoc_words != []:
        a_row.append(assoc_words)
        a_row.append(sentence_string)
        list_to_return.append(a_row)
    return list_to_return

def out_to_csv(list, csv_file):
    with open(csv_file, 'wb') as g:
        writer = csv.writer(g, delimiter='\t')
        w = csv.writer(g)

        # Add a header
        w.writerow(["Character ID", "Associated Words", "Sentence"])

        # Output values to csv
        for row in list:
            w.writerow(row)

def create_word_character_matrix(outDir, text):
    global final_output

    print("---- Creating character word association matrix for: " + text + " ----")

    in_file = outDir + "/" + text + "/bookNLP/BookNLP.csv"
    md_file = outDir + "/" + text + "/bookNLP/metadata.csv"

    # ADD A FLAG TO FLIP OFF THE OUTPUT OF THESE 4 TEST CSVS. JUST IN CASE
    # PEOPLE ONLY WANT THE FINAL OUTPUT AND NOT THIS DEBUGGING EXTRA STUFF.
    debug_path = outDir + "/" + text + "/debug/"
    if not os.path.exists(debug_path):
        os.makedirs(debug_path)
    out_file_agent = outDir + "/" + text + "/debug/characters_agent.csv"
    out_file_patient = outDir + "/" + text + "/debug/characters_patient.csv"
    out_file_poss = outDir + "/" + text + "/debug/characters_possession.csv"
    out_file_mod = outDir + "/" + text + "/debug/characters_modification.csv"
    out_file_matrix = outDir + "/" + text + "/character_associated_words.csv"

    word_count = 0

    # Get the total word count from the metadata.csv file
    with open(md_file, 'rb') as f:
        reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            if (row[0] == "Total Words"):
                word_count = int(row[1])
        if (word_count == 0):
            print("There was an error reading the metadata.csv file!")
            sys.exit()

    # Create the associations.csv file!
    sentence = []
    char_assoc_agent = []
    char_assoc_patient = []
    char_assoc_poss = []
    char_assoc_mod = []
    char_in_sentence = False
    sentenceID = '0'
    with open(in_file, 'rb') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        # Skip the header
        next(reader, None)
        for row in reader:
            #Break sentence based on NLP sentence IDs and quotation marks.
            if row[1] != sentenceID or row[10] == '``' or row[10] == "''":
                sentenceID = row[1]

                # If no character is in the sentence, skip.
                if not char_in_sentence:
                    sentence = []
                    sentence.append(row)
                    continue

                # DEBUG CODE: Reconstitute the sentence roughly, to show what
                # we're looking at.
                sentence_string = ""
                for item in sentence:
                    sentence_string += str(item[7]) + " "

                # Scan for patient relationships.
                char_assoc_patient += patient(sentence, sentence_string)

                # Scan for possession relationships.
                char_assoc_poss += possession(sentence, sentence_string)

                # Scan for modification relationships.
                char_assoc_mod += modification(sentence, sentence_string)

                # Scan for agent relationships.
                # (Done last because it changes the words in sentence.)
                char_assoc_agent += agent(sentence, sentence_string)

                sentence = []
                char_in_sentence = False

            if row[11] == 'PERSON':
                char_in_sentence = True
            sentence.append(row)

    out_to_csv(char_assoc_agent, out_file_agent)
    out_to_csv(char_assoc_patient, out_file_patient)
    out_to_csv(char_assoc_poss, out_file_poss)
    out_to_csv(char_assoc_mod, out_file_mod)

    # Output the 2 dimensional dictionary of characters and words to a csv file
    fields = []
    for key in final_output.keys() :
        fields.extend(final_output[key].keys())
    # this removes duplicates but destroys order
    fields = list(set(fields))

    fields = ['Character'] + fields

    with open(out_file_matrix,'wb') as out_file:
        w = csv.DictWriter(out_file, fields)
        w.writeheader()
        for key,val in sorted(final_output.items()):
            row = {'Character': key}

            # Normalize word occurrences by total number of words in text.
            for k, v in val.items():
                val[k] = float(v)/word_count

            row.update(val)
            w.writerow(row)

    print("---- Character word association matrix created. ----")
