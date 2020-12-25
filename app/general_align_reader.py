from app.align_reader import AlignReader
import codecs
import os
from app.utils import LOG, Cache
import pickle
import collections

class GeneralAlignReader(AlignReader):

	def __init__(self, config_path=""): 
		AlignReader.__init__(self, config_path)
		if config_path == "":
			config_path = "/mounts/work/ayyoob/alignment/config/"

		self.alignment_path = "/mounts/work/ayyoob/alignment/output/eflomal_aligns/"
		self.index_path = "/mounts/work/ayyoob/alignment/output/"
		self.prefix_file = "/mounts/work/mjalili/projects/pbc_simalign/configs/prefixes.txt"
		self.all_langs = []
		self.lang_files = {}

		self.read_prefix_file()
		self.content_cache = Cache(self.read_alignment_file)
		self.indexes_cache = Cache(self.read_index_file)
		self.lang_name_file_mapping = collections.OrderedDict(sorted(self.read_dict_file(config_path + "language_name_file_mapping.txt").items()))
		self.file_lang_name_mapping = collections.OrderedDict(sorted(self.read_dict_file(config_path + "file_language_name_mapping.txt").items()))
		self.index_size = 121447 #TODO put me in config

	def setup_dict_entry(self, _dict, entry, val):
		if entry not in _dict:
			_dict[entry] = val

	def read_dict_file(self, file_path, do_lower=False):
		res = {}
		with open(file_path, "r") as mapping_list:
			for l in mapping_list:
				if l.startswith('#'):
					continue 
				

				if do_lower:
					l.lower()

				# print(l.strip())
				pair = l.strip().split('\t')
				
				res[pair[0].strip()] = pair[1].strip()
				print(pair)
		return res

	def read_prefix_file(self):
		
		with open(self.prefix_file, "r") as prf_file:
			for prf_l in prf_file:
				prf_l = prf_l.strip().split()
				file_name = prf_l[0]
				lang_name = file_name[:3] #TODO fixme and all first 3 char considerations!
				
				if lang_name not in self.lang_files:
					self.lang_files[lang_name] = [file_name]
				else:
					self.lang_files[lang_name].append(file_name)

		self.all_langs = list(self.lang_files.keys())

	def get_source_target_order(self, lang_1, lang_2):
		for lang in self.all_langs:
			if lang == lang_1:
				return  (lang_1, lang_2)
			if lang == lang_2:
				return (lang_2, lang_1)

	def get_ordered_langs(self, edition_1, edition_2):
		lang_1 = edition_1[:3]
		lang_2 = edition_2[:3]

		s_lang, t_lang = self.get_source_target_order(lang_1, lang_2)

		# if not os.path.exists(self.get_align_file_path(s_lang, t_lang)):
		# 	print("WARNING alignment file for expected order of following languages not found, change order", s_lang, t_lang)
		# 	tmp = t_lang
		# 	t_lang = s_lang
		# 	s_lang = tmp

		if s_lang == lang_1:
			return s_lang, t_lang, edition_1, edition_2
		else:
			return s_lang, t_lang, edition_2, edition_1

	def get_align_file_path(self, lang1, lang2):
		src_lang, trg_lang, src_edition, trg_edition = self.get_ordered_langs(lang1, lang2)
		return "{}/{}_{}_word.inter".format(self.alignment_path, src_edition, trg_edition) 
	def get_index_file_path(self, lang1, lang2):
		src_lang, trg_lang, src_edition, trg_edition = self.get_ordered_langs(lang1, lang2)
		return "%s/index_%s_%s.txt" % (self.index_path, src_edition, trg_edition) 
	
	def get_index_key(self, index, verse, s_file, t_file):
		if s_file in index:
			if t_file in index[s_file]:
				if verse in index[s_file][t_file]:
					return index[s_file][t_file][verse]
		return -1

	def read_alignment_file(self, file_path):
		res = []
		with open(file_path, 'r') as f:
			for line in f:
				s_l = line.split('\t') # handle index at the begining of the line
				if len(s_l) > 1:
					res.append(s_l[1])
				else:
					res.append(s_l[0])
		
		return res 

	def get_hash(self, verse):
		res = int(verse) #TODO fixme for strings
		return res

	def add_to_index(self, index, key, val, to_send):
		loc = self.get_hash(key) % self.index_size
		next_count = 0
		if index[loc] == None:
			index[loc] = {"key":key, "val":val, "next":None}
		else:
			last = index[loc]
			if to_send != None:
				LOG.info("verse {}, hash {}, loc {}, index {}".format(key, self.get_hash(key), loc, to_send))
			while last["next"] != None:
				next_count += 1
				last = last["next"]
			last["next"] = {"key":key, "val":val, "next":None}
		return next_count
	
	def get_from_index(self, index, key):
		loc = self.get_hash(key) % self.index_size
		res = index[loc]

		while res != None:
			if res["key"] == key:
				return res["val"]
			res = res["next"]
		
		return None

	def read_index_file(self, file_path):
		LOG.info("reading index file ({})".format(file_path))
		first_inex = None
		res = {}
		next_count = 0
		with open(file_path, 'r') as f: 
			for i, line in enumerate(f):
				verse, s_edition, t_edition = tuple(line.strip().split('\t'))
				self.setup_dict_entry(res, s_edition, {})

				self.setup_dict_entry(res[s_edition], t_edition, {})
				res[s_edition][t_edition][verse] = i
				# if t_edition not in res[s_edition]:
				# 	res[s_edition][t_edition] = [None for i in range(self.index_size)]
				# if first_inex == None:
				# 	first_inex = s_edition + " " + t_edition
				# to_send = None if first_inex != s_edition + " " + t_edition else first_inex
				# next_count += self.add_to_index(res[s_edition][t_edition], verse, i, to_send)

			# LOG.info("reading index file next_count: {}, tot_lines{}, source_count: {}, target_count:{}".format(next_count, i, len(res.keys()), sum([len(res[x].keys()) for x in res])))
				
		
		return res

	def create_ordered_alignment(self, alignments, index_key, revert):
		alignment_line = alignments[index_key].split()
		alignment_line = [x.split('-') for x in alignment_line]

		align = [] 
		for x in alignment_line:
			align.append((int(x[1]), int(x[0])) if revert else (int(x[0]), int(x[1])) )

		return align

	def get_verse_alignment(self, verse_nums, edition_1, edition_2, alignments_loc=None, index_loc=None):
		aligns = {}

		if edition_1[:3] == edition_2[:3]:
			return aligns

		if edition_1 in self.bert_langs and edition_2 in self.bert_langs:
			LOG.info("going to super aglingment for: {}, {}".format(edition_1, edition_2 ))
			return super().get_verse_alignment(verse_nums, self.lang_prf_map[edition_1], self.lang_prf_map[edition_2])

		LOG.info("getting eflomal aglingment for: {} , {}".format(edition_1, edition_2) ) 
		s_lang, t_lang, s_edition, t_edition = self.get_ordered_langs(edition_1, edition_2)
		revert = False
		if s_edition == edition_2:
			revert = True
		
		LOG.info("copying")
		if alignments_loc == None:
			alignments = self.content_cache.get(self.get_align_file_path(s_lang, t_lang))
		else:
			with open("./af", "rb") as af:
				alignments = pickle.load(af)
		if index_loc == None:
			index = self.indexes_cache.get(self.get_index_file_path(s_lang, t_lang))
		else:
			with open("./if", "rb") as iif:
				index = pickle.load(iif)

		if s_edition in index:
			if t_edition in index[s_edition]:
				index = index[s_edition][t_edition]

		LOG.info("getting verses" )  
		for verse in verse_nums:
			# index_key = self.get_index_key(index, verse, s_edition, t_edition)
			# index_key = self.get_from_index(index, verse)
			# if index_key != None:
			# 	aligns[verse] = self.create_ordered_alignment(alignments, index_key, revert) 

			if verse in index:
				aligns[verse] = self.create_ordered_alignment(alignments, index[verse], revert) 
		LOG.info("verses got")
		return aligns

	def get_verse_alignment_mp(self, verse_nums, edition_pairs, alignments_loc=None, index_loc=None):
		res = []
		counter = 0
		for edition_1, edition_2 in edition_pairs:
			aligns = {}

			if edition_1[:3] == edition_2[:3]:
				res.append((edition_1, edition_2, aligns))
				continue

			if edition_1 in self.bert_langs and edition_2 in self.bert_langs:
				LOG.info("going to super aglingment for: {}, {}".format(edition_1, edition_2 ))
				res.append((edition_1, edition_2, super().get_verse_alignment(verse_nums, self.lang_prf_map[edition_1], self.lang_prf_map[edition_2])))
				continue

			LOG.info("getting eflomal aglingment for: {} , {}".format(edition_1, edition_2) ) 
			s_lang, t_lang, s_edition, t_edition = self.get_ordered_langs(edition_1, edition_2)
			revert = False
			if s_edition == edition_2:
				revert = True
			
			if counter == 0:
				LOG.info("copying")
				if alignments_loc == None:
					alignments = self.content_cache.get(self.get_align_file_path(s_lang, t_lang))
				else:
					with open(alignments_loc, "rb") as af:
						alignments = pickle.load(af)
				if index_loc == None:
					index_t = self.indexes_cache.get(self.get_index_file_path(s_lang, t_lang))
				else:
					with open(index_loc, "rb") as iif:
						index_t = pickle.load(iif)
				counter = 1

			if s_edition in index_t:
				if t_edition in index_t[s_edition]:
					index = index_t[s_edition][t_edition]

			LOG.info("getting verses" )  
			for verse in verse_nums:
				# index_key = self.get_index_key(index, verse, s_edition, t_edition)
				# index_key = self.get_from_index(index, verse)
				# if index_key != None:
				# 	aligns[verse] = self.create_ordered_alignment(alignments, index_key, revert) 

				if verse in index:
					aligns[verse] = self.create_ordered_alignment(alignments, index[verse], revert) 
			LOG.info("verses got")
			res.append((edition_1, edition_2, aligns))
		return res


