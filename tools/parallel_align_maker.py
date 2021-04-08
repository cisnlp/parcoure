import os, sys
import os.path
import regex
import codecs
import collections
from random import shuffle
import concurrent.futures
import logging
import time
import argparse
from app import utils 
from app.general_align_reader import GeneralAlignReader




def log_state(src_lang, trg_lang, state):
	logging.info(F"alignment process of {src_lang},{trg_lang} {state}")

def align_editions(lang_name, files):
	log_state(lang_name, lang_name, "starting, files:%d" % len(files) )
	
	if os.path.exists("{}/{}_word.inter".format(output_path, lang_name)) or len(files) < 2:
		log_state(lang_name, lang_name, "early abort")
		return
	
	#if os.path.exists("{}/{}_word.inter".format(output_path, lang_name)):
	#	os.remove("{}/{}_word.inter".format(output_path, lang_name))
	#	os.remove("{}/{}_word.fwd".format(output_path, lang_name))
	#	os.remove("{}/{}_word.rev".format(output_path, lang_name))

	src_sentences = utils.read_files(files)
	trg_sentences = dict(src_sentences)
	
	align_file_path = "{}/{}_word".format(output_path, lang_name)
	intersect_file = "%s/sentences_%s.txt" % (output_path, lang_name) 
	index_file = "%s/index_%s.txt" % (index_path, lang_name) 

	#------------------------------------ create fastaling format parallel text and index file -----------------------------
	tot_intersect_sentences = 0
	with codecs.open(intersect_file, "w", "utf-8") as ictf, codecs.open(index_file, "w", "utf-8") as idxf:

		for sfile in src_sentences:
			del trg_sentences[sfile]
			for verse in src_sentences[sfile]:
				for tfile in trg_sentences:
					if verse in trg_sentences[tfile]:
						tot_intersect_sentences += 1
						ictf.write(src_sentences[sfile][verse] + " ||| " + trg_sentences[tfile][verse] + "\n")
						idxf.write(verse + "\t" + sfile + "\t" + tfile + "\n")
						
	#---------------------------------- call align extractor ---------------------------------------------------------------
	log_state(lang_name, lang_name, "going to align %d lines" % tot_intersect_sentences)
	os.system(F"python -u -m tools.extract_alignments -p {intersect_file} -m {aligner} -o {align_file_path}")
	os.remove(intersect_file)
	log_state(lang_name, lang_name, "end")

def align_languages(src_lang_name, trg_lang_name, src_files, trg_files):
	l1, l2 = align_reader.get_ordered_langs(src_lang_name, trg_lang_name)
	if l1 == trg_lang_name:
		src_lang_name = l1
		trg_lang_name = l2
		tmp = src_files
		src_files = trg_files
		trg_files = tmp
		
	log_state(src_lang_name, trg_lang_name, "starting, sfiles:%d, tfiles: %d" % (len(src_files), len(trg_files)) )

	if os.path.exists("{}/{}_{}_word.inter".format(output_path, src_lang_name, trg_lang_name)):
		log_state(src_lang_name, trg_lang_name, "early abort")
		return

	src_sentences = utils.read_files(src_files)
	trg_sentences = utils.read_files(trg_files)
	
	align_file_path = "{}/{}_{}_word".format(output_path, src_lang_name, trg_lang_name)
	intersect_file = "%s/sentences_%s_%s.txt" % (output_path, src_lang_name, trg_lang_name) 
	index_file = "%s/index_%s_%s.txt" % (index_path, src_lang_name, trg_lang_name) 

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
	os.system(F"python -u -m tools.extract_alignments -p {intersect_file} -m {aligner} -o {align_file_path}")
	#os.remove(intersect_file)
	log_state(src_lang_name, trg_lang_name, "end")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="extract the alignments for languages mentioned in lang_files.txt file."\
		"-s start number, -e end number, -o alignment output dir, -i alignments index dir, -a aligner (sim_align, other)", 
	epilog="example: python eflomal_align_maker.py -s 0 -e 200, -o /output -i /index -a other")
	parser.add_argument("-s", default=0)
	parser.add_argument("-e", default=sys.maxsize)
	parser.add_argument("-o", default="")
	parser.add_argument("-i", default="")
	parser.add_argument("-a", default="sim_align")
	parser.add_argument("-w", default=1)

	utils.setup(os.environ['CONFIG_PATH'])
	align_reader = GeneralAlignReader()

	args = parser.parse_args()
	if  args.o == "" or args.i == "":
		print("Please specify index and output dirs")
		exit()
	
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

	aligner = args.a
	output_path = args.o
	index_path = args.i


	lang_files = align_reader.lang_files
	all_langs = align_reader.all_langs

	logging.info("language count: %d", len(all_langs))
	logging.info("files count: %d", sum([len(x) for x in lang_files.values()]))



	a_slang = []
	a_tlang = []
	a_sfiles = []
	a_tfiles = []
	a_lang_files = []
	for i, s_lang in enumerate(all_langs):
		a_lang_files.append(lang_files[s_lang])
		if i < int(args.s) or i>int(args.e):
			continue
		for t_lang in all_langs[i+1:]:
			a_slang.append(s_lang)
			a_tlang.append(t_lang)
			a_sfiles.append(lang_files[s_lang])
			a_tfiles.append(lang_files[t_lang])

	with concurrent.futures.ThreadPoolExecutor(max_workers=int(args.w)) as executor:
		executor.map(align_languages, a_slang, a_tlang, a_sfiles, a_tfiles)
		executor.map(align_editions, all_langs, a_lang_files)