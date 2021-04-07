import logging
import multiprocessing
import codecs
import sys
import configparser
import os, subprocess



def get_logger(name, filename, level=logging.DEBUG):
	logger = logging.getLogger(name)
	logger.setLevel(level)

	fh = logging.FileHandler(filename)
	ch = logging.StreamHandler()

	fh.setLevel(level)
	ch.setLevel(level)

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)

	logger.addHandler(ch)
	logger.addHandler(fh)

	return logger

config_dir = ""
corpora_dir = ""
CIS = False
lang_file_mapping_path = ""
es_index_url = ""
es_index_url_noedge = ""
stats_directory = ""
config_parser = ""
alignments_dir = ""
simalign_corpus_dir = ""
lexicon_dir = ""
LOG = get_logger("analytics", "logs/analytics.log")

def setup(f):
	global config_parser
	global config_dir
	global corpora_dir
	global lang_file_mapping_path
	global es_index_url
	global es_index_url_noedge
	global stats_directory
	global alignments_dir
	global simalign_corpus_dir
	global lexicon_dir

	if not os.path.exists(f):
		print(f"Cannot find config file at {f}")
		exit()
		
	config_parser = configparser.ConfigParser()
	config_parser.read(f)

	config_dir = config_parser['section']['config_dir']
	corpora_dir = config_parser['section']['corpora_dir']
	if not os.path.exists("logs"):
		os.mkdir("logs")

	lang_file_mapping_path = config_dir + "lang_files.txt"

	es_index_url = config_parser['section']['elasticsearch_address'] + "/" + config_parser['section']['index_name']
	es_index_url_noedge = config_parser['section']['elasticsearch_address'] + "/" + config_parser['section']['noedge_index_name']
	stats_directory = config_parser['section']['stats_dir']
	alignments_dir = config_parser['section']['alignments_dir']
	simalign_corpus_dir = config_parser['section']['simalign_corpus_dir']
	lexicon_dir = config_parser['section']['lexicon_dir']

def synchronized_method(method):
	
	outer_lock = multiprocessing.Lock()
	lock_name = "__"+method.__name__+"_lock"+"__"
	
	def sync_method(self, *args, **kws):
		with outer_lock:
			if not hasattr(self, lock_name): setattr(self, lock_name, multiprocessing.Lock())
			lock = getattr(self, lock_name)
			with lock:
				return method(self, *args, **kws)  

	return sync_method


class Cache():

	def __init__(self, retriever, cache_size=1000):
		self.cache_keys = []
		self.cache = {}
		self.retriever = retriever
		self.cache_size = cache_size
		
	@synchronized_method
	def get(self, key):
		if key in self.cache_keys:
			self.cache_keys.remove(key)
			self.cache_keys.append(key)
		else:
			self.cache[key] = self.retriever(key)
			self.cache_keys.append(key)

			if len(self.cache_keys) > self.cache_size:
				to_remove_key = self.cache_keys.pop(0)
				del self.cache[to_remove_key]

		return self.cache[key] 


def read_dict_file_data(f_path):
	res = {}
	min = sys.maxsize
	max = -min -1
	with codecs.open(f_path, 'r', "utf-8") as f:
		for line in f:
			parts = line.split('\t')
			if len(parts) == 2 or len(parts) == 3:
				if len(parts) == 2:
					val = int(parts[1])
					key = parts[0]
				else:
					val = int(parts[2])
					key = parts[0] + "  " + parts[1]
				res[key] = val
				if val > max:
					max = val
				if val < min:
					min = val

	return (res, min, max)

def setup_dict_entry(_dict, entry, val):
	if entry not in _dict:
		_dict[entry] = val


def read_files(editions):
	res = {}
	for f in editions:
		res[f] = {}
		if os.path.exists(corpora_dir + '/' + f + ".txt"):
			with codecs.open(corpora_dir + '/' + f + ".txt", "r", "utf-8") as fi:
				for l in fi:
					if l[0] == "#":
						continue
					l = l.strip().split("\t")
					if len(l) != 2:
						continue
					res[f][l[0]] = l[1]
		else:
			LOG.warning(f"file {corpora_dir + f}.txt not found")
	return res 

def read_lang_file_mapping():
	lang_files = {}

	try:
		with open(lang_file_mapping_path, "r") as prf_file:
			for prf_l in prf_file:
				prf_l = prf_l.strip().split()
				file_name = prf_l[0]
				lang_name = prf_l[1] 
				
				if lang_name not in lang_files:
					lang_files[lang_name] = [file_name]
				else:
					lang_files[lang_name].append(file_name)
	except FileNotFoundError as e:
		LOG.warning("Language files mapping file not found")

	all_langs = list(lang_files.keys())
	all_langs.sort()

	return lang_files, all_langs


def run_command(cmd):
	"""Run command, return output as string."""
	subprocess.Popen(cmd, shell=True).communicate()[0]
