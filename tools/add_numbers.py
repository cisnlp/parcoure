#!/usr/bin/env python3
import codecs
import argparse

def add_numbers(input_file, output_file, start=0, max_num=-1):
	with codecs.open(input_file, "r", "utf-8") as fi, codecs.open(output_file, "w", "utf-8") as fo:
		count = start
		for l in fi:
			fo.write(str(count) + "\t" + l.strip() + "\n")
			count += 1
			if max_num > 0 and count >= max_num:
				break

def remove_numbers(input_file, output_file):
	with codecs.open(input_file, "r", "utf-8") as fi, codecs.open(output_file, "w", "utf-8") as fo:
		for l in fi:
			l = l.strip().split("\t")
			if len(l) < 2:
				l = ["", ""]
			fo.write(l[1] + "\n")


if __name__ == "__main__":
	'''
	Add line numbers, TAB separated. 
	The start index can be changed by "-start" (Default value is 0). 
	The maximum index can be changed by "--max_num" (Default value is -1 which means all lines).

	usage: python add_numbers.py input_file output_file [--max_num x] [-start y]
	'''

	parser = argparse.ArgumentParser(description="Add line numbers, TAB separated.", epilog="example: python add_numbers.py input output")
	parser.add_argument("input")
	parser.add_argument("output")
	parser.add_argument("--max_num", type=int, default=-1)
	parser.add_argument("-start", type=int, default=0)
	parser.add_argument("--remove_num", action="store_true")
	args = parser.parse_args()

	if args.remove_num:
		remove_numbers(args.input, args.output)
	add_numbers(args.input, args.output, args.start, args.max_num)
