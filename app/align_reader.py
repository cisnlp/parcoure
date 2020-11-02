import codecs


class AlignReader(object):
	def __init__(self, config_path=""):
		self.pbc_path = "/nfs/datc/pbc/"
		self.align_path = "/mounts/work/mjalili/projects/pbc_simalign/output/"
		if config_path == "":
			config_path = "/mounts/work/mjalili/projects/pbc_simalign/configs/"

		#-------------------------- ayyoob, file lang name mapping -------------
		self.file_lang_name_mapping = {}
		with open(config_path + "file_language_name_mapping.txt", "r") as mapping_list:
			for l in mapping_list:
				if l.startswith('#'):
					continue
				pair = l.strip().split('\t')
				self.file_lang_name_mapping[pair[0].strip()] = pair[1].strip()

				
		#-------------------------- ayyoob, lanugage name file mapping -------------
		self.lang_name_file_mapping = {}
		with open(config_path + "language_name_file_mapping.txt", "r") as mapping_list:
			for l in mapping_list:
				if l.startswith('#'):
					continue
				pair = l.strip().split('\t')
				print(pair)
				self.lang_name_file_mapping[pair[0].strip().lower()] = pair[1].strip()

		#-------------------------- collect translation names ------------------------------
		self.all_langs = []
		with open(config_path + "bert_100.txt", "r") as lang_list:
			for l in lang_list:
				if l.startswith("#"):
					continue
				self.all_langs.append(l.strip())

		#-------------------------- loading translations prefixes --------------------------
		self.lang_prf_map = {}
		self.prf_lang_map = {}
		with open(config_path + "prefixes.txt", "r") as prf_file:
			for prf_l in prf_file:
				prf_l = prf_l.strip().split()
				self.lang_prf_map[prf_l[0]] = prf_l[1]
				self.prf_lang_map[prf_l[1]] = prf_l[0]

		#-------------------------- collect verses -----------------------------------------
		self.ids = {}
		self.ids["trn"] = []
		self.ids["tst"] = []
		self.ids["dev"] = []
		self.ids["all"] = []

		with open(config_path + "numversesplit.txt", "r") as ids_file:
			for l in ids_file:
				l = l.strip().split()
				self.ids[l[0]].append(l[1])
				self.ids["all"].append(l[1])

	#ayyoob
	def get_text_for_lang(self, lang):
		sentences = {}
		with codecs.open(self.pbc_path + lang + ".txt", "r", "utf-8") as src_file:
			for l in src_file:
				if l[0] == "#":
					continue
				l = l.strip().split("\t")
				if len(l) != 2:
					continue
				if l[0] in self.ids["all"]:
					sentences[l[0]] = l[1]
		return sentences

	def sort_lang_pair(self, l_pair):
		s, t = l_pair
		if s in self.prf_lang_map:
			if self.all_langs.index(self.prf_lang_map[s]) < self.all_langs.index(self.prf_lang_map[t]):
				return l_pair, False
			else:
				return (t, s), True
		else:
			if self.all_langs.index(s) < self.all_langs.index(t):
				return (self.lang_prf_map[s], self.lang_prf_map[t]), False
			else:
				return (self.lang_prf_map[t], self.lang_prf_map[s]), True

	def find_word(self, q_word, q_lang="engq"):
		if q_lang not in self.prf_lang_map:
			print("Language prefix not found.")
			return None

		q_sentences = {}
		with codecs.open(self.pbc_path + self.prf_lang_map[q_lang] + ".txt", "r", "utf-8") as src_file:
			for l in src_file:
				if l[0] == "#":
					continue
				l = l.strip().split("\t")
				if len(l) != 2:
					continue
				if l[0] in self.ids["all"] and q_word in l[1].lower():
					q_sentences[l[0]] = ([i for i, w in enumerate(l[1].split()) if w.lower() == q_word], l[1])
		return q_sentences

	def get_text_for_prf(self, lang):
		if lang not in self.prf_lang_map:
			print("Language prefix not found.")
			return None

		sentences = {}
		with codecs.open(self.pbc_path + self.prf_lang_map[lang] + ".txt", "r", "utf-8") as src_file:
			for l in src_file:
				if l[0] == "#":
					continue
				l = l.strip().split("\t")
				if len(l) != 2:
					continue
				if l[0] in self.ids["all"]:
					sentences[l[0]] = l[1]
		return sentences

	def get_intersect_verse_nums(self, lang_1, lang_2):
		lang_pair, switched = self.sort_lang_pair((lang_1, lang_2))

		f_path = self.align_path + F"verse_files/{lang_pair[0]}_{lang_pair[1]}.verses"
		verses = []
		with open(f_path, "r") as f_align:
			for l in f_align:
				verses.append(l.strip())
		return verses

	def get_verse_alignment(self, verse_nums, lang_1, lang_2):
		lang_pair, switched = self.sort_lang_pair((lang_1, lang_2))
		order = [0, 1]
		if switched:
			order = [1, 0]

		f_path = self.align_path + F"bert_aligns/{lang_pair[0]}_{lang_pair[1]}_bpe.inter"
		aligns = {}
		with open(f_path, "r") as f_align:
			for al_l in f_align:
				al_l = al_l.strip().split("\t")
				if al_l[0] in verse_nums:
					line = [(int(p.split("-")[order[0]]), int(p.split("-")[order[1]])) for p in al_l[1].split()]
					aligns[al_l[0]] = sorted(line)
		return aligns

	@staticmethod
	def add_word_index(sentences):
		if isinstance(sentences[0], str):
			sentences = [s.split() for s in sentences]

		sentences = [" ".join([F"{i}:{w}" for i, w in enumerate(s)]) for s in sentences]
		return sentences

# --------------------------------------------------------
# --------------------------------------------------------
if __name__ == "__main__":
	print("Example Usage:")
	ar = AlignReader()

	# written = []
	# with open("language_file_mapping.txt", 'w') as f:
	# 	for fname in ar.all_langs:
	# 		if fname[:3] == "nob":
	# 			f.write("%s\t%s\n" % (fname, "Norwegian"))
	# 		else:
	# 			f.write("%s\t%s\n" % (fname, ar.lang_name_mapping[fname[:3]]))
	# 			# written.append(prf[:3])

	eng_sents = ar.get_text_for_prf("engq")
	deu_sents = ar.get_text_for_prf("deui")
	ende_verses = ar.get_intersect_verse_nums("engq", "deui")

	aligns = ar.get_verse_alignment(ende_verses[:10], "engq", "deui")
	tuples = [(v, ar.add_word_index([eng_sents[v], deu_sents[v]]), aligns[v]) for v in ende_verses[:10]]

	print(tuples[0])
	print(tuples[1])
