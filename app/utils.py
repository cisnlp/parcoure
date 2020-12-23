import logging
import multiprocessing

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
		
	# @synchronized_method  
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


CIS = False
LOG = get_logger("analytics", "logs/analytics.log")


es_index_url = "http://127.0.0.1:9200/bible_index"
es_index_url_noedge = "http://127.0.0.1:9200/bible_index_noedge"
