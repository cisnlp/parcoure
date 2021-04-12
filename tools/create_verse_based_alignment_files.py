import os
from app import utils
from app.general_align_reader import GeneralAlignReader

align_reader = GeneralAlignReader()
verse_file_contents = {}

def process_language_pair_verses(a_file, i_file): 
    ###
    # receives an alignment and an index file and update the verse_file_contents structure
    # a_file: alignment_file
    # i_file: alignments index file
    ###
    
    print(f"going to process {a_file}, {i_file}")
    
    with open(a_file, 'r') as afl, open(i_file, 'r') as ifl:
        a_lines = afl.readlines()
        i_lines = ifl.readlines()

        for tup in zip(a_lines, i_lines):
            aligns = tup[0].strip()
            verse, s_edit, t_edit = tuple(tup[1].strip().split())
            utils.setup_dict_entry(verse_file_contents, verse, "")
            verse_file_contents[verse] += f"{s_edit}\t{t_edit}\t{aligns}\n"
    
def persist_verse_contents():
    print(f"going to persist {len(verse_file_contents)} verses")
    for verse in verse_file_contents:
        with open(f"{utils.alignInduction.verse_alignments_path}/{verse}.txt", 'a') as f:
            f.write(verse[verse])

def process_batch_of_language_pairs(lang_pairs):
    ###
    # for a batch of language pair update ver_file_contents dictionary and finally flushes the 
    # dictionary to files
    ###

    print(f"processing a batch of language pairs with size of {len(lang_pairs)}")

    for pair in lang_pairs:
        s_l, t_l = align_reader.get_ordered_langs(pair[0], pair[1])
        a_file = align_reader.get_align_file_path(s_l, t_l)
        i_file = align_reader.get_index_file_path(s_l, t_l)
        process_language_pair_verses(a_file, i_file)

    persist_verse_contents()
    print(f"finished processing a batch of language pairs with size of {len(lang_pairs)}")


if __name__ == "__main__":
    utils.setup(os.environ['CONFIG_PATH'])
    _, langs = utils.read_lang_file_mapping()

    all_pairs = [[]]
    counter = 0
    for i,l1 in enumerate(langs):
        for l2 in langs[i:]:
            all_pairs[-1].append([l1, l2])
            counter += 1
            if counter % 1000 == 0 :
                all_pairs.append([])

    print(f"processing {len(all_pairs)} pair batches of languages")
    
    for pair_batch in all_pairs:
        process_batch_of_language_pairs(pair_batch)