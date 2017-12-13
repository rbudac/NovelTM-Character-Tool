# Uses Python 2

import os
import sys
import subprocess
import re

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def totalWords(fname):
    num_words = 0
    with open(fname, 'r') as f:
        for line in f:
            words = line.split()
            num_words += len(words)
    return num_words



# Directory variables
#bookNLPPath = "book-nlp"
bookNLP = "./runjava"
#coreNLPPath = "core-nlp"
#coreNLP = "stanford-corenlp-3.6.0.jar"
#outDir = "out"


def run_bookNLP(bookNLPPath, outDir, text_path, text_filename):

    # Check to see if bookNLP and coreNLP are installed. Exit if not.
    if not os.path.isfile(bookNLPPath + "/" + bookNLP):
        print("BookNLP was not found. Please install.")
        sys.exit()
    #if not os.path.isfile(coreNLPPath + "/" + coreNLP):
    #     print("coreNLP was not found. Please install.")
    #     sys.exit()

    # bookNLP needs to be run from it's directory, so the output must be directed back out of the directory.
    bookNLPParam = "novels/BookNLP -doc ../" + text_path + " -printHTML -p ../" + outDir + "/" + text_filename + "/bookNLP/ -tok ../" 
    bookNLPParam = bookNLPParam + outDir + "/" + text_filename + "/bookNLP/" + "BookNLP.csv -f >> ../out.txt 2>&1 -id "
    bookNLPParam = bookNLPParam + "BookNLP"

    print("\n---- Running BookNLP on: " + text_filename + " ----\n")

    # Run BookNLP
#    with cd("./book-nlp"):
    with cd(bookNLPPath):
        print subprocess.check_output([bookNLP,bookNLPParam])

    # Output total word count to a metadata.csv file
    with open(outDir + "/" + text_filename + "/bookNLP/metadata.csv", 'w') as f:
        words_str = "Total Words," + str(totalWords(text_path))
        f.write(words_str)

    print("---- BookNLP process complete. ----")

