#!/usr/bin/env python3
import codecs
import argparse, configparser
import os.path
import os
# from . import add_numbers
from tools import add_numbers


def create_alignment(src_path="", trg_path="", paral_path="", out_path="", model="fast_align"):
	# create parallel text
	if paral_path == "":
		paral_path = out_path + ".txt"

		fa_file = codecs.open(paral_path, "w", "utf-8")
		fsrc = codecs.open(src_path, "r", "utf-8")
		ftrg = codecs.open(trg_path, "r", "utf-8")

		for sl, tl in zip(fsrc, ftrg):
			sl = sl.strip()
			tl = tl.strip()

			if len(sl.split("\t")) == 2:
				sl = sl.split("\t")[1]
			if len(tl.split("\t")) == 2:
				tl = tl.split("\t")[1]

			fa_file.write(sl + " ||| " + tl + "\n")
		fa_file.close()

	# FastAlign
	if model == "fast_align":
		os.system("{} -i {} -v -d -o > {}.fwd".format(fastalign_path, paral_path, out_path))
		os.system("{} -i {} -v -d -o -r > {}.rev".format(fastalign_path, paral_path, out_path))
	# Eflomal
	elif model == "other": # we consider it eflomal
		os.system(eflomal_path + "align.py -i {0} --model 3 -f {1}.fwd -r {1}.rev".format(paral_path, out_path))

	os.system("{0} -i {1}.fwd -j {1}.rev -c grow-diag-final-and > {1}_unnum.gdfa".format(atools_path, out_path))
	add_numbers.add_numbers(out_path + "_unnum.gdfa", out_path + ".gdfa")
	os.system("rm {}_unnum.gdfa".format(out_path))

	with open(out_path + ".fwd", "r") as f1, open(out_path + ".rev", "r") as f2, open(out_path + ".inter", "w") as fo:
		count = 0
		for l1, l2 in zip(f1, f2):
			l1 = set(l1.strip().split())
			l2 = set(l2.strip().split())
			fo.write(str(count) + "\t" + " ".join(sorted([x for x in l1 & l2])) + "\n")
			count += 1


if __name__ == "__main__":
	'''
	Extract alignments with different models and store in files.
	The output_file is set by "-o" and is the path and name of the output file without extension.
	The alignment model is set by "-m". The options are "fast" for Fastalign and "eflomal".
	Input files can either be two separate source and target files, or a single parallel file in Fastalign format.

	usage 1: ./extract_alignments.py -s file1 -t file2 -o output_file
	usage 2: ./extract_alignments.py -p parallel_file -o output_file

	example: ./extract_alignments.py -p data/eng_deu.txt -m fast -o alignments/eng_deu
	'''

	parser = argparse.ArgumentParser(description="Extract alignments with different models and store in files.", 
	epilog="example: python extract_alignments.py -s file1 -t file2 -o output_file")

	parser.add_argument("-s", default="", help="source path")
	parser.add_argument("-t", default="", help="target path")
	parser.add_argument("-p", help="parallel text in fastalign format (if available)", default="")
	parser.add_argument("-o", help="the output_file path and name without extension")
	parser.add_argument("-m", choices=['fast_align', 'other'], default="fast_align")

	args = parser.parse_args()
	if args.s == "" and args.t == "" and args.p == "":
		print("No input is given.")
		exit()

	config_file = os.environ['CONFIG_PATH']
	parser = configparser.ConfigParser()
	parser.read(config_file)

	eflomal_path = parser['section']['extra_aligner_path'] + "/"
	fastalign_path = parser['section']['fast_align_path'] + "/fast_align"
	atools_path = parser['section']['fast_align_path'] + "/atools"

	create_alignment(args.s, args.t, args.p, args.o, args.m)

