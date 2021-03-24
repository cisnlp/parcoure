from app.general_align_reader import GeneralAlignReader
from app.document_retrieval import DocumentRetriever
from datetime import datetime
from app.utils import LOG, Cache
from multiprocessing import Pool
import math
import os
from copy import deepcopy
from random import shuffle

import pickle

align_reader = GeneralAlignReader()
doc_retriever = DocumentRetriever()


class Lexicon(object):

    def __init__(self, lexicon_path=""):
        if lexicon_path != "":
            self.lexicon_path = lexicon_path
        else:
            self.lexicon_path = "/mounts/work/ayyoob/alignment/output/lexicon/"
        
        self.lexicon_cache = Cache(self.read_lexicon)
        
    def lexicon_file(self, src_lang, trg_lang):
        return self.lexicon_path + "/" + src_lang + "_" + trg_lang + ".txt"

    def read_lexicon(self, path):
        LOG.info("reading lexicon: " + path)
        with open(path, 'rb') as inf:
            return pickle.load(inf)

    def get_from_pre_computed_lexicon(self, src_lang, trg_lang, word):
        """[summary]

        Args:
            src_lang ([type]): [description]
            trg_lang ([type]): [description]
            word ([type]): [description]

        Returns:
            dictionary: {translation_in_trg_lang : {"count":2, "verses":[...], "trg_editions":[...]}
        """

        if not os.path.exists(self.lexicon_file(src_lang, trg_lang)):
            return None
        
        lexicon = self.lexicon_cache.get(self.lexicon_file(src_lang, trg_lang))

        if word not in lexicon:
            return {}

        res = deepcopy(lexicon[word])

        

        for trg_word in res:
            trg_editions = align_reader.lang_files[trg_lang][:]
            if len(trg_editions) > 4:
                shuffle(trg_editions)
                trg_editions = trg_editions[:4]
            res[trg_word]["trg_editions"] = trg_editions

        return res

        

    def keep_only_containing_verses(self, docs, term, source_langauge):
        verses = []
        final_docs = {}
        for doc in docs['hits']['hits']:
            tokens = doc["_source"]["content"].split()
            doc['termIndexes'] = [i for i,t in enumerate(tokens) if t.lower()==term.lower()]
            if len(doc['termIndexes']) > 0 and doc['_source']['language'][:3] == source_langauge:
                if doc["_source"]["verse_id"] not in verses:
                    verses.append(doc["_source"]["verse_id"])
                if doc['_source']['language'] not in final_docs:
                    final_docs[doc['_source']['language']] = []
                final_docs[doc['_source']['language']].append(doc)
        return final_docs, verses

    def get_translations(self, term, source_lang, target_langs):
        """[summary]

        Args:
            term (string): a single term to find the translation for
            source_lang (string): 3 letter lang name
            target_langs (list): list of 3 letter target lang name

        Returns:
            dictionary: of shape {target_lang : {translation_in_trg_lang : {"count":2, "verses":[...], "trg_editions":[...]}} }
        """
        target_langs_copy = target_langs[:]
        res = {}

        for target_lang in target_langs_copy[:]:
            if source_lang == target_lang:
                target_langs_copy.remove(target_lang)

            if self.get_from_pre_computed_lexicon(source_lang, target_lang, term) != None:
                res[target_lang] = self.get_from_pre_computed_lexicon(source_lang, target_lang, term)
                target_langs_copy.remove(target_lang)
        
        if len(target_langs_copy) == 0:
            return res
        
        LOG.info(1)
        docs = doc_retriever.search_documents(term + " " + source_lang.strip()+"-x-bible",
            all_docs=True, prefixed_search=True)
        LOG.info(2)
        
        docs, verses = self.keep_only_containing_verses(docs, term, source_lang)
        LOG.info("sourcee lang verses: {}, {}".format(source_lang, len(verses)))
            
        for target_lang in target_langs_copy:

            res[target_lang] = {} 
            doc_ids = []
            LOG.info(3) 
            for target_edition in align_reader.lang_files[target_lang]:
                doc_ids.extend([verse + "@" + target_edition for verse in verses])
            target_docs = doc_retriever.retrieve_multi_docs(doc_ids)
            LOG.info("target doc count: {}".format(len(target_docs)))
            LOG.info(4)
            all_verses_alignments = {}


            per_processor = 10 #TODO make me config
            cpu_count = math.floor((len(align_reader.lang_files[source_lang]) * len(align_reader.lang_files[target_lang]))/10) + 1
            LOG.info(5)
            alignments = []
            args = []
            edition_pairs = [] 
            for source_edition in align_reader.lang_files[source_lang]:
                for target_edition in align_reader.lang_files[target_lang]:
                    edition_pairs.append((source_edition, target_edition))
                    if (len(edition_pairs) == per_processor):
                        args.append((verses[:], edition_pairs[:]))
                        edition_pairs = []
                    # alignments.append(align_reader.get_verse_alignment(verses, source_edition, target_edition))

            if len(edition_pairs) > 0:
                args.append((verses[:], edition_pairs[:])) #TODO fixme
                
            with Pool(cpu_count) as p:  
                alignment_groups = p.starmap(align_reader.get_verse_alignment_mp, args) 
            
            for group in alignment_groups:
                for item in group:
                    alignments.append(item[2])
            LOG.info(6)

            i = 0
            for source_edition in align_reader.lang_files[source_lang]:
                all_verses_alignments[source_edition] = {}
                for target_edition in align_reader.lang_files[target_lang]:
                    all_verses_alignments[source_edition][target_edition] = alignments[i]
                    i += 1
            LOG.info(7)

            for source_edition in align_reader.lang_files[source_lang]:
                if source_edition in docs:
                    for doc in docs[source_edition]: 
                        verse = doc["_source"]["verse_id"]
                        for target_edition, verses_alignments in all_verses_alignments[source_edition].items():
                            if verse in verses_alignments.keys():  
                                target_positins = [s for f,s in verses_alignments[verse] if f in doc['termIndexes']]
                            
                                if len(target_positins) > 0 and verse+"@"+target_edition in target_docs : #FIXME inconsistency in elasticsearch and alignment files 
                                    taget_tokens = target_docs[verse+"@"+target_edition].split()
                                    
                                    for target_positin in target_positins:
                                        token = taget_tokens[target_positin]
                                        if token in res[target_lang]:
                                            res[target_lang][token]['count'] += 1
                                            if res[target_lang][token]['count'] < 50:
                                                res[target_lang][token]['verses'].append(doc["_id"])
                                                if target_edition not in res[target_lang][token]['trg_editions']:
                                                    res[target_lang][token]['trg_editions'].append(target_edition) 
                                        else:
                                            res[target_lang][token] = {'count':1, 'verses':[doc["_id"]], 'trg_editions':[target_edition]} 

        return res
