import os
import os.path
import regex
import codecs
import collections
from random import shuffle
import concurrent.futures
import logging
import time
import argparse
from app.utils import read_files, read_lang_file_mapping



pbc_path = "/nfs/datc/pbc/"
# aligner_path = "python /mounts/Users/student/masoud/Dokumente/code/pbc_utils/extract_alignments.py"
aligner_path = "python /mounts/Users/student/masoud/pbc_utils/extract_alignments.py"
output_path = "/mounts/work/ayyoob/alignment/output/"


def log_state(src_lang, trg_lang, state):
	logging.info(F"alignment process of {src_lang},{trg_lang} {state}")

def align_languages(src_lang_name, trg_lang_name, src_files, trg_files):
	log_state(src_lang_name, trg_lang_name, "starting, sfiles:%d, tfiles: %d" % (len(src_files), len(trg_files)) )

	if os.path.exists("{}/{}_aligns/{}_{}_word.inter".format(output_path,aligner, src_lang_name, trg_lang_name)):
		log_state(src_lang_name, trg_lang_name, "early abort")
		return

	src_sentences = read_files(src_files)
	trg_sentences = read_files(trg_files)
	
	align_file_path = "{}{}_aligns/{}_{}_word".format(output_path, aligner, src_lang_name, trg_lang_name)
	intersect_file = "%s/sentences_%s_%s.txt" % (output_path, src_lang_name, trg_lang_name) 
	index_file = "%s/index_%s_%s.txt" % (output_path, src_lang_name, trg_lang_name) 

	#------------------------------------ create fastaling format parallel text and index file -----------------------------
	tot_intersect_sentences = 0
	with codecs.open(intersect_file, "w", "utf-8") as ictf, codecs.open(index_file, "w", "utf-8") as idxf:

		for sfile in src_sentences:
			for verse in src_sentences[sfile]:
				for tfile in trg_sentences:
					if verse in trg_sentences[tfile]:
						tot_intersect_sentences += 1
						ictf.write(src_sentences[sfile][verse] + " ||| " + trg_sentences[tfile][verse] + "\n")
						idxf.write(verse + "\t" + sfile + "\t" + tfile + "\n")
						
	#---------------------------------- call align extractor ---------------------------------------------------------------
	log_state(src_lang_name, trg_lang_name, "going to align %d lines" % tot_intersect_sentences)
	os.system(aligner_path + F" -p {intersect_file} -m {aligner} -o {align_file_path}")
	os.remove(intersect_file)
	log_state(src_lang_name, trg_lang_name, "end")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="extract the alignments for languages mentioned in lang_files.txt file.", 
	epilog="example: python eflomal_align_maker.py -s 0 -e 200")
	parser.add_argument("-s", default="")
	parser.add_argument("-e", default="")

	args = parser.parse_args()
	if args.s == "" or args.e == "" :
		print("No input is given.")
		exit()
	
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

	aligner = "eflomal"

	lang_files, _ = read_lang_file_mapping()
	all_langs = list(lang_files.keys())

	logging.info("language count: %d", len(all_langs))
	logging.info("files count: %d", sum([len(x) for x in lang_files.values()]))

	a_slang = []
	a_tlang = []
	a_sfiles = []
	a_tfiles = []
	for i, s_lang in enumerate(all_langs):
		if i < int(args.s) or i>int(args.e):
			continue
		for t_lang in all_langs[i+1:]:
			a_slang.append(s_lang)
			a_tlang.append(t_lang)
			a_sfiles.append(lang_files[s_lang])
			a_tfiles.append(lang_files[t_lang])

	with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
		executor.map(align_languages, a_slang, a_tlang, a_sfiles, a_tfiles)




