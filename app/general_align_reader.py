from app.align_reader import AlignReader
import codecs
import os
from app.utils import LOG, Cache, config_path as utils_config_path, read_lang_file_mapping
from multiprocessing import Manager
import pickle
import collections

m = Manager()
index_lock = m.Lock()
alignments_lock = m.Lock()

class GeneralAlignReader(AlignReader):

	def __init__(self, config_path=""): 
		AlignReader.__init__(self, config_path)
		if config_path == "":
			config_path = utils_config_path 

		self.alignment_path = "/mounts/work/ayyoob/alignment/output/eflomal_aligns/"
		self.index_path = "/mounts/work/ayyoob/alignment/output/"
		self.lang_order_file_path = config_path + "/langauges_order_file.txt"
		self.lang_orders = self.read_langs_order_file()

		self.lang_files, self.all_langs = read_lang_file_mapping()
		self.content_cache = Cache(self.read_alignment_file)
		self.indexes_cache = Cache(self.read_index_file)
		self.edition_file_mapping = collections.OrderedDict(sorted(self.read_dict_file(config_path + "edition_file_mapping.txt").items()))
		self.file_edition_mapping = collections.OrderedDict(sorted(self.read_dict_file(config_path + "file_edition_mapping.txt").items()))
		self.index_size = 121447 #TODO put me in config
		
	def read_langs_order_file(self):
		res = []
		with open(self.lang_order_file_path, 'r') as inf:
			for l in inf:
				res.append(l.strip())
		return res

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

				pair = l.strip().split('\t')
				
				res[pair[0].strip()] = pair[1].strip()
				print(pair)
		return res

	def get_source_target_order(self, lang_1, lang_2):
		if lang_1 + "," + lang_2 in self.lang_orders:
			return lang_1, lang_2
		else:
			return lang_2,lang_1


	def get_ordered_langs(self, edition_1, edition_2):
		lang_1 = edition_1[:3] # TODO fixme
		lang_2 = edition_2[:3] # TODO fixme

		s_lang, t_lang = self.get_source_target_order(lang_1, lang_2)

		if s_lang == lang_1:
			return s_lang, t_lang, edition_1, edition_2
		else:
			return s_lang, t_lang, edition_2, edition_1

	def get_align_file_path(self, edition_1, edition_2):
		src_lang, trg_lang, _, _ = self.get_ordered_langs(edition_1, edition_2)
		return "{}/{}_{}_word.inter".format(self.alignment_path, src_lang, trg_lang) 

	def get_align_binary_file_path(self, edition_1, edition_2):
		return "%s.binary" % self.get_align_file_path(edition_1, edition_2)

	def get_index_file_path(self, edition_1, edition_2):
		src_lang, trg_lang, _, _ = self.get_ordered_langs(edition_1, edition_2)
		return "%s/index_%s_%s.txt" % (self.index_path, src_lang, trg_lang) 
	
	def get_index_binary_file_path(self, edition_1, edition_2):
		return "%s.pickle" % self.get_index_file_path(edition_1, edition_2)

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
		res = {}
		with open(file_path, 'r') as f: 
			for i, line in enumerate(f):
				verse, s_edition, t_edition = tuple(line.strip().split('\t'))
				self.setup_dict_entry(res, s_edition, {})

				self.setup_dict_entry(res[s_edition], t_edition, {})
				res[s_edition][t_edition][verse] = i
	
		return res

	def create_index_binary_file_if_not_exists(self, lang1, lang2):
		index_lock.acquire()
		if not os.path.exists(self.get_index_binary_file_path(lang1, lang2)):
			LOG.info("creating binary index file for {}, {}".format(lang1, lang2))
			ind = self.read_index_file(self.get_index_file_path(lang1, lang2))
			with (open(self.get_index_binary_file_path(lang1, lang2), 'wb')) as of:
				pickle.dump(ind, of)
		index_lock.release()
	
	def create_align_binary_file_if_not_exists(self, lang1, lang2):
		alignments_lock.acquire()
		if not os.path.exists(self.get_align_binary_file_path(lang1, lang2)):
			LOG.info("creating binary alignments file for {}, {}".format(lang1, lang2))
			aln = self.read_alignment_file(self.get_align_file_path(lang1, lang2))
			with (open(self.get_align_binary_file_path(lang1, lang2), 'wb')) as of:
				pickle.dump(aln, of)
		alignments_lock.release()
	
	def get_alignment(self, lang1, lang2):
		self.create_align_binary_file_if_not_exists(lang1, lang2)
		with open(self.get_align_binary_file_path(lang1, lang2), 'rb') as inf:
			res = pickle.load(inf)
		return res

	def get_index(self, lang1, lang2):
		self.create_index_binary_file_if_not_exists(lang1, lang2)
		with open(self.get_index_binary_file_path(lang1, lang2), 'rb') as inf:
			res = pickle.load(inf)
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

		if edition_1 in self.bert_files and edition_2 in self.bert_files:
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
			if verse in index:
				aligns[verse] = self.create_ordered_alignment(alignments, index[verse], revert) 
		LOG.info("verses got")
		return aligns

	def get_verse_alignment_mp(self, verse_nums, edition_pairs):
		res = []
		ps_lang, pt_lang, index_t, alignments = None, None, None, None # if we have multiple edition pairs of the same languages, we use prev loaded files!
		for edition_1, edition_2 in edition_pairs:
			aligns = {}

			if edition_1[:3] == edition_2[:3]:
				res.append((edition_1, edition_2, aligns))
				continue

			if edition_1 in self.bert_files and edition_2 in self.bert_files:
				LOG.info("going to super aglingment for: {}, {}".format(edition_1, edition_2 ))
				res.append((edition_1, edition_2, super().get_verse_alignment(verse_nums, self.lang_prf_map[edition_1], self.lang_prf_map[edition_2])))
				continue

			LOG.info("getting eflomal aglingment for: {} , {}".format(edition_1, edition_2) ) 
			s_lang, t_lang, s_edition, t_edition = self.get_ordered_langs(edition_1, edition_2)

			revert = False
			if s_edition == edition_2:
				revert = True
			
			if s_lang != ps_lang or t_lang != pt_lang:
				alignments = self.get_alignment(s_lang, t_lang)
				index_t = self.get_index(s_lang, t_lang)
				ps_lang, pt_lang = s_lang, t_lang

			index = None
			if s_edition in index_t:
				if t_edition in index_t[s_edition]:
					index = index_t[s_edition][t_edition]
			
			if index is not None:

				LOG.info("getting verse, {}, {}, {}, {}, {}, {}, {}, {}".format( edition_1, edition_2, s_lang, t_lang, ps_lang, pt_lang, len(index_t), len(index)))
				for verse in verse_nums:
					if verse in index:
						aligns[verse] = self.create_ordered_alignment(alignments, index[verse], revert) 
				LOG.info("verses got")
				
			else: 
				LOG.warning("couldn't find index for: " + s_edition + ", " + t_edition)
				
			res.append((edition_1, edition_2, aligns))
		return res