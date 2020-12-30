from app.general_align_reader import GeneralAlignReader as AlignReader
import os

align_reader = AlignReader()

with open(align_reader.lang_order_file_path, 'w') as of:
    for i,lang1 in enumerate(align_reader.all_langs):
        for lang2 in align_reader.all_langs[i+1:]:
            if os.path.exists("{}/{}_{}_word.inter".format(align_reader.alignment_path, lang1, lang2)):
                of.write(lang1 + "," + lang2 + "\n")
            else:
                of.write(lang2 + "," + lang1 + "\n")



