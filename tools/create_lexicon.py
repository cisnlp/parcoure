import argparse
from app.utils import read_files
from app.general_align_reader import GeneralAlignReader 
from app.lexicon import Lexicon
from app.utils import setup_dict_entry
import pickle


align_reader = GeneralAlignReader()
lexicon = Lexicon()

def log_counter(counter):
    if counter % 10000 == 0:
        print(counter)
    counter += 1

def get_lexicon(l1_verses, l2_verses, alignments, index):
    lang_1_lexicon = {}
    lang_2_lexicon = {}
    print("alignments size", len(alignments))
    counter = 0
    for i in range(len(alignments)):
        log_counter(counter)
        counter += 1
        alignment = align_reader.create_ordered_alignment(alignments, i, False)
        verse = index[i][0]
        verse_l1 = index[i][0] + '@' + index[i][1]
        verse_l2 = index[i][0] + '@' + index[i][2]

        l1_verse_content = l1_verses[index[i][1]][verse].split()
        l2_verse_content = l2_verses[index[i][2]][verse].split()
        for aligned_words in alignment:
            l1_word = l1_verse_content[aligned_words[0]]
            l2_word = l2_verse_content[aligned_words[1]]
            setup_dict_entry(lang_1_lexicon, l1_word, {})
            setup_dict_entry(lang_2_lexicon, l2_word, {})
            setup_dict_entry(lang_1_lexicon[l1_word], l2_word, {"count":0, "verses":[]})
            setup_dict_entry(lang_2_lexicon[l2_word], l1_word, {"count":0, "verses":[]})
            lang_1_lexicon[l1_word][l2_word]["count"] += 1
            lang_2_lexicon[l2_word][l1_word]["count"] += 1
            if len(lang_1_lexicon[l1_word][l2_word]["verses"]) < 50:
                lang_1_lexicon[l1_word][l2_word]["verses"].append(verse_l1)
            if len(lang_2_lexicon[l2_word][l1_word]["verses"]) < 50:
                lang_2_lexicon[l2_word][l1_word]["verses"].append(verse_l2)
    return lang_1_lexicon,lang_2_lexicon

def read_index_file(lang_1, lang_2):
    file_path = align_reader.get_index_file_path(lang_1, lang_2)
    print("reading index file ({})".format(file_path))
    res = []
    with open(file_path, 'r') as f: 
        for line in f:
            verse, s_edition, t_edition = tuple(line.strip().split('\t'))
            res.append((verse, s_edition, t_edition))
    return res

def save_lexicons(lang_1_2_lexicon, lang_2_1_lexicon, lang_1, lang_2):
    with open(lexicon.lexicon_path+"/"+lang_1+"_"+lang_2+".txt", 'wb') as of:
        pickle.dump(lang_1_2_lexicon, of)

    with open(lexicon.lexicon_path+"/"+lang_2+"_"+lang_1+".txt", 'wb') as of:
        pickle.dump(lang_2_1_lexicon, of)

def create_lexicon_for_lang_pair(lang_1, lang_2):
    lang_1, lang_2, _, _ = align_reader.get_ordered_langs(lang_1, lang_2)
    print("getting pbc data", lang_1, lang_2)
    l1_verses = read_files(align_reader.lang_files[lang_1])
    l2_verses = read_files(align_reader.lang_files[lang_2])

    print("getting alignments", lang_1, lang_2)
    alignments = align_reader.get_alignment(lang_1, lang_2)
    print("getting index", lang_1, lang_2)
    index = read_index_file(lang_1, lang_2)

    print("getting lexicon", lang_1, lang_2)
    lang_1_2_lexicon, lang_2_1_lexicon = get_lexicon(l1_verses, l2_verses, alignments, index)

    print("saving lexicon", lang_1, lang_2)
    save_lexicons(lang_1_2_lexicon, lang_2_1_lexicon, lang_1, lang_2)

def read_languages_file(file):
    res = []
    with open(file, 'r') as inf:
        for line in inf:
            line = line.strip()
            if not line.startswith("#"):
                langs = (line.split(',')[0], line.split(',')[1])
                res.append(langs)
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extract a lexicon for languages mentioned in the input file file.", 
    epilog="example: python create_lexicon.py -f my_language_pairs.txt")
    parser.add_argument("-f", default="")

    args = parser.parse_args()
    if args.f == "":
        print("No input is given.")
        exit()
    
    langauge_pairs = read_languages_file(args.f)

    for lang_pair in langauge_pairs:
        create_lexicon_for_lang_pair(lang_pair[0], lang_pair[1])