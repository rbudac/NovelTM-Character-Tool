# Uses Python 2 -_- Look into switching to 3
import os
import sys
sys.path.insert(0, './scripts')

import bookNLP
import charTable
import charWordMatrix
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Extracts characters and associated words from texts.')
    parser.add_argument("-s", "--skip", help="Skip a step. Steps are: \"1\" BookNLP")
    parser.add_argument("-b", "--bookNLP", default="book-nlp", help="Specifiy a path for where to find BookNLP. Default is \"book-nlp\"")
    parser.add_argument("-d", "--directory", default="texts", help="Specify a directory containing text files. Default is \"texts\"")
    parser.add_argument("-o", "--out", default="out", help="Specify an output directory. Default is \"out\"")
    args = parser.parse_args()

    textsPath = args.directory
    textDir = os.listdir(textsPath) # returns list
    texts = []

    for file in textDir:
        # Ensure that only text files are included:
        if file.endswith(".txt"):
            text_dir = os.path.join(textsPath, file)
            texts.append(text_dir)

    print("Texts Found:")
    for text in texts:
        text_fn = os.path.basename(os.path.splitext(text)[0])
        print(text_fn)
    print("")

    # IMPLEMENT A LOOP HERE TO GO OVER ALL FILES
    for text in texts:
        text_fn = os.path.basename(os.path.splitext(text)[0])

        if args.skip != '1':
            bookNLP.run_bookNLP(args.bookNLP, args.out, text, text_fn)
        charTable.create_char_table(args.out, text_fn)
        charWordMatrix.create_word_character_matrix(text_fn)
        print("---- Done with: " + text + "! ----\n")

    print("Done!")
