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
from app.utils import read_files



pbc_path = "/nfs/datc/pbc/"
alignment_path = "/mounts/work/ayyoob/alignment/output/eflomal_aligns/"
prefix_file = "/mounts/work/mjalili/projects/pbc_simalign/configs/prefixes.txt"

language_token_stats_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_token_stats.txt"
edition_token_stats_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_token_stats.txt"
lang_verse_stat_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_verse_stats.txt"
edition_verse_stat_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_verse_stats.txt"
lang_pair_token_count_stats_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_pair_token_count_stats.txt"
lang_pair_token_totcount_stats_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_pair_token_totcount_stats.txt"
edition_pair_token_count_stats_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_pair_token_count_stats.txt"
edition_pair_token_totcount_stats_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_pair_token_totcount_stats.txt"
lang_pair_verse_stat_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_pair_verse_stats.txt"
edition_pair_verse_stat_file = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_pair_verse_stats.txt"

lang_pair_stats_dir = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_pair_stats"
edition_pair_stats_dir = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_pair_stats"
lang_stats_dir = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/lang_stats"
edition_stats_dir = "/mounts/work/ayyoob/alignment_stats/efomal_aligns/edition_stats"

all_langs = []
def get_source_target_order(lang1, lang2):
	for lang in all_langs:
		if lang == lang1:
			return  (lang1, lang2)
		if lang == lang2:
			return (lang2, lang1)

def setup_dict_entry(_dict, entry, val):
	if entry not in _dict:
		_dict[entry] = val

def read_alignment_file(file_path):
	res = []
	with open(file_path, 'r') as f:
		for line in f:
			s_l = line.split('\t') # handle index
			if len(s_l) > 1:
				res.append(s_l[1])
			else:
				res.append(s_l[0])
	
	return res

def add_tokens(tokens, token_dict):
	for t in tokens:
		setup_dict_entry(token_dict, t, 0)
		token_dict[t] += 1

def add_edition_tokens(tokens, edition_dict, edition):
	setup_dict_entry(edition_dict, edition, {})
	add_tokens(tokens, edition_dict[edition])

def write_dict_data_to_file(file_path, data, mode):
	with open(file_path, mode) as of:
			for key in data:
				of.write(str(key) + "\t" + str(data[key]) + "\n")
				
def log_state(src_lang, trg_lang, state):
	logging.info(F"alignment process of {src_lang},{trg_lang} {state}")

def get_in_order(lang_name1, lang_name2, files1, files2, store_lang1_stat, store_lang2_stat):
	s_lang, t_lang = get_source_target_order(lang_name1, lang_name2)
	if s_lang == lang_name1:
		return (lang_name1, lang_name2, files1, files2, store_lang1_stat, store_lang2_stat)
	elif t_lang == lang_name1:
		return (lang_name2, lang_name1, files2, files1, store_lang2_stat, store_lang1_stat)

def compute_alignment_statics(lang_name1, lang_name2, files1, files2, store_lang1_stat, store_lang2_stat):
	src_lang_name, trg_lang_name, src_files, trg_files, store_slang_stat, store_tlang_stat = get_in_order(lang_name1, lang_name2, files1, files2, store_lang1_stat, store_lang2_stat)
	
	log_state(src_lang_name, trg_lang_name, "starting, sfiles:%d, tfiles: %d" % (len(src_files), len(trg_files)) )

	if os.path.exists("{}/{}_{}_tokens_stat.txt".format(lang_pair_stats_dir,src_lang_name, trg_lang_name)):
		log_state(src_lang_name, trg_lang_name, "early abort")
		return
	src_sentences = read_files(src_files)
	trg_sentences = read_files(trg_files)

	src_lang_tokens = {}
	target_lang_tokens = {}
	src_edition_tokens = {}
	target_edition_tokens = {}

	lang_pair_freqs = {}
	edition_pair_freqs = {}
	lang_pair_verse_count = 0
	edition_pair_verse_count = {}

	alignments = read_alignment_file("{}/{}_{}_word.inter".format(alignment_path, src_lang_name, trg_lang_name))

	#----------------------------- calculating stats -------------------------------------------#
	log_state(src_lang_name, trg_lang_name, "calculating stats")

	for sfile in src_sentences:
			for verse in src_sentences[sfile]:
				s_terms = src_sentences[sfile][verse].split()
				add_tokens(s_terms, src_lang_tokens)
				add_edition_tokens(s_terms, src_edition_tokens, sfile)
				for tfile in trg_sentences:
					if verse in trg_sentences[tfile]:
						t_terms = trg_sentences[tfile][verse].split()
						aling_pairs = alignments[lang_pair_verse_count].split()
						
						edition_pair = sfile + "_" + tfile
						setup_dict_entry(edition_pair_verse_count, edition_pair, 0)
						edition_pair_verse_count[edition_pair] += 1
						setup_dict_entry(edition_pair_freqs, edition_pair, {})
						

						for align_pair in aling_pairs:
							indices = [ int(x) for x in align_pair.split('-') ]
							term_pair = s_terms[indices[0]] + '\t' + t_terms[indices[1]]

							setup_dict_entry(lang_pair_freqs, term_pair, 0)
							lang_pair_freqs[term_pair] += 1
							setup_dict_entry(edition_pair_freqs[edition_pair], term_pair, 0)
							edition_pair_freqs[edition_pair][term_pair] += 1

						lang_pair_verse_count += 1

	if store_tlang_stat:
		for tfile in trg_sentences:
			for verse in trg_sentences[tfile]:
				# print(tfile, verse)
				# print(trg_sentences[tfile][verse])
				t_terms = trg_sentences[tfile][verse].split()
				add_tokens(t_terms, target_lang_tokens)
				add_edition_tokens(t_terms, target_edition_tokens, tfile)

	#-------------------------------- writing stats -----------------------------------------#
	log_state(src_lang_name, trg_lang_name, "writing stats")
	# try:
	if store_slang_stat:
		write_dict_data_to_file(language_token_stats_file, {src_lang_name: len(src_lang_tokens)}, 'a')
		write_dict_data_to_file("{}/{}_tokens_stat.txt".format(lang_stats_dir, src_lang_name), src_lang_tokens, 'w')

		write_dict_data_to_file(edition_token_stats_file, {x: len(src_edition_tokens[x]) for x in src_edition_tokens}, 'a')
		for edition in src_edition_tokens:
			write_dict_data_to_file("{}/{}_tokens_stat.txt".format(edition_stats_dir, edition), src_edition_tokens[edition], 'w')
		
		write_dict_data_to_file(lang_verse_stat_file, {src_lang_name: sum([len(src_sentences[x]) for x in src_sentences])}, 'a')
		write_dict_data_to_file(edition_verse_stat_file, {x: len(src_sentences[x]) for x in src_sentences}, 'a')
	
	if store_tlang_stat:
		write_dict_data_to_file(language_token_stats_file, {trg_lang_name: len(target_lang_tokens)}, 'a')
		write_dict_data_to_file("{}/{}_tokens_stat.txt".format(lang_stats_dir, trg_lang_name), target_lang_tokens, 'w')

		write_dict_data_to_file(edition_token_stats_file, {x: len(target_edition_tokens[x]) for x in target_edition_tokens}, 'a')
		for edition in target_edition_tokens:
			write_dict_data_to_file("{}/{}_tokens_stat.txt".format(edition_stats_dir, edition), target_edition_tokens[edition], 'w')
		
		write_dict_data_to_file(lang_verse_stat_file, {trg_lang_name: sum([len(trg_sentences[x]) for x in trg_sentences])}, 'a')
		write_dict_data_to_file(edition_verse_stat_file, {x: len(trg_sentences[x]) for x in trg_sentences}, 'a')
	
	write_dict_data_to_file(lang_pair_token_count_stats_file, {"{}_{}".format(src_lang_name, trg_lang_name): len(lang_pair_freqs)}, 'a')
	write_dict_data_to_file(lang_pair_token_totcount_stats_file, {"{}_{}".format(src_lang_name, trg_lang_name): sum(lang_pair_freqs.values())}, 'a')
	write_dict_data_to_file("{}/{}_{}_tokens_stat.txt".format(lang_pair_stats_dir,src_lang_name, trg_lang_name), lang_pair_freqs, 'w')

	for edition_pair in edition_pair_freqs:
		write_dict_data_to_file(edition_pair_token_count_stats_file, {edition_pair:len(edition_pair_freqs[edition_pair])}, 'a')
		write_dict_data_to_file(edition_pair_token_totcount_stats_file, {edition_pair:sum(edition_pair_freqs[edition_pair].values())}, 'a')
		write_dict_data_to_file("{}/{}_tokens_stat.txt".format(edition_pair_stats_dir,edition_pair), edition_pair_freqs[edition_pair], 'w')

	write_dict_data_to_file(lang_pair_verse_stat_file, {"{}_{}".format(src_lang_name, trg_lang_name): lang_pair_verse_count}, 'a')
	write_dict_data_to_file(edition_pair_verse_stat_file, edition_pair_verse_count, 'a')
	# except Exception as exc:
	# 	logging.error("error while writing stats : %s", exc)
	log_state(src_lang_name, trg_lang_name, "end")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="compute alignment statistics for languages mentioned in prefixes.txt file.", 
	epilog="example: python eflomal_align_maker.py -s 0 -e 200 \n python eflomal_align_maker.py -l eng")
	parser.add_argument("-s", default="")
	parser.add_argument("-e", default="")
	parser.add_argument("-l", default="")


	
	args = parser.parse_args()
	if args.s == "" or args.e == "" :
		if args.l == "":
			print("No input is given.")
			exit()
	
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

	#-------------------------- loading translations prefixes --------------------------
	lang_files = {}
	with open(prefix_file, "r") as prf_file:
		for prf_l in prf_file:
			prf_l = prf_l.strip().split()
			file_name = prf_l[0]
			lang_name = file_name[:3]
			
			if lang_name not in lang_files:
				lang_files[lang_name] = [file_name]
			else:
				lang_files[lang_name].append(file_name)

	all_langs = list(lang_files.keys())

	logging.info("language count: %d", len(all_langs))
	logging.info("files count: %d", sum([len(x) for x in lang_files.values()]))

	a_slang = []
	a_tlang = []
	a_sfiles = []
	a_tfiles = []
	s_lang_store = []
	t_lang_store = []
	if args.l != "":
		if args.l not in all_langs:
			logging.error("bad language selected")
		else:
			for i, t_lang in enumerate(all_langs):
				if t_lang != args.l:
					a_slang.append(args.l)
					a_tlang.append(t_lang)
					a_sfiles.append(lang_files[args.l])
					a_tfiles.append(lang_files[t_lang])
					t_lang_store.append(True)
					if i == 0:
						s_lang_store.append(True)
						compute_alignment_statics(args.l, t_lang, lang_files[args.l], lang_files[t_lang], True, True)
					else:
						s_lang_store.append(False)
						compute_alignment_statics(args.l, t_lang, lang_files[args.l], lang_files[t_lang], False, True)

	else:
		for i, s_lang in enumerate(all_langs):
			if i < int(args.s) or i>int(args.e):
				continue
			for j, t_lang in enumerate(all_langs[i+1:]):
				a_slang.append(s_lang)
				a_tlang.append(t_lang)
				a_sfiles.append(lang_files[s_lang])
				a_tfiles.append(lang_files[t_lang])

				t_lang_store.append(False)
				if j == 0:
					s_lang_store.append(True)
				else:
					s_lang_store.append(False)


		with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
			for r in executor.map(compute_alignment_statics, a_slang, a_tlang, a_sfiles, a_tfiles, s_lang_store, t_lang_store):
				try:
					print(r)
				except Exception as exc:
					print('generated an exception: %s' % (exc))



