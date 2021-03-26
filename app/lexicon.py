from app.general_align_reader import GeneralAlignReader
from app.document_retrieval import DocumentRetriever
from datetime import datetime
from app import utils
from multiprocessing import Pool
import math
import os
from copy import deepcopy
from random import shuffle

import pickle

align_reader = GeneralAlignReader()
doc_retriever = DocumentRetriever()


class Lexicon(object):

    def __init__(self):
        self.lexicon_path = utils.lexicon_dir
        
        self.lexicon_cache = utils.Cache(self.read_lexicon)
        
    def lexicon_file(self, src_lang, trg_lang):
        return self.lexicon_path + "/" + src_lang + "_" + trg_lang + ".txt"

    def read_lexicon(self, path):
        utils.LOG.info("reading lexicon: " + path)
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
            trg_lang_files = align_reader.lang_files[trg_lang][:]
            if len(trg_lang_files) > 4:
                shuffle(trg_lang_files)
                trg_lang_files = trg_lang_files[:4]
            res[trg_word]["trg_editions"] = trg_lang_files

        return res

        

    def keep_only_containing_verses(self, docs, term, source_langauge):
        verses = []
        final_docs = {}
        for doc in docs['hits']['hits']:
            tokens = doc["_source"]["content"].split()
            doc['termIndexes'] = [i for i,t in enumerate(tokens) if t.lower()==term.lower()]
            if len(doc['termIndexes']) > 0 and align_reader.file_lang_mapping[doc['_source']['language']] == source_langauge:
                if doc["_source"]["verse_id"] not in verses:
                    verses.append(doc["_source"]["verse_id"])
                if doc['_source']['language'] not in final_docs:
                    final_docs[doc['_source']['language']] = []
                final_docs[doc['_source']['language']].append(doc)
        return final_docs, verses
    
    def get_lang_string(self, lang):
        res = ""
        for f in align_reader.lang_files[lang]:
            res += f + " "
        
        return res.strip()

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
        
        utils.LOG.info(1)
        docs = doc_retriever.search_documents(term ,
            all_docs=True, prefixed_search=True, language=self.get_lang_string(source_lang))
        utils.LOG.info(2)
        
        docs, verses = self.keep_only_containing_verses(docs, term, source_lang)
        utils.LOG.info("sourcee lang verses: {}, {}".format(source_lang, len(verses)))
            
        for target_lang in target_langs_copy:

            res[target_lang] = {} 
            doc_ids = []
            utils.LOG.info(3) 
            for target_lang_file in align_reader.lang_files[target_lang]:
                doc_ids.extend([verse + "@" + target_lang_file for verse in verses])
            target_docs = doc_retriever.retrieve_multi_docs(doc_ids)
            utils.LOG.info("target doc count: {}".format(len(target_docs)))
            utils.LOG.info(4)
            all_verses_alignments = {}


            per_processor = 10 #TODO make me config
            cpu_count = math.floor((len(align_reader.lang_files[source_lang]) * len(align_reader.lang_files[target_lang]))/10) + 1
            utils.LOG.info(5)
            alignments = []
            args = []
            edition_pairs = [] 
            for source_lang_file in align_reader.lang_files[source_lang]:
                for target_lang_file in align_reader.lang_files[target_lang]:
                    edition_pairs.append((align_reader.file_edition_mapping[source_lang_file], align_reader.file_edition_mapping[target_lang_file]))
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
            utils.LOG.info(6)

            i = 0
            for source_lang_file in align_reader.lang_files[source_lang]:
                all_verses_alignments[source_lang_file] = {}
                for target_lang_file in align_reader.lang_files[target_lang]:
                    all_verses_alignments[source_lang_file][target_lang_file] = alignments[i]
                    i += 1
            utils.LOG.info(7)

            for source_lang_file in align_reader.lang_files[source_lang]:
                if source_lang_file in docs:
                    for doc in docs[source_lang_file]: 
                        verse = doc["_source"]["verse_id"]
                        for target_lang_file, verses_alignments in all_verses_alignments[source_lang_file].items():
                            if verse in verses_alignments.keys():  
                                target_positins = [s for f,s in verses_alignments[verse] if f in doc['termIndexes']]
                            
                                if len(target_positins) > 0  and verse+"@"+target_lang_file in target_docs: 
                                    taget_tokens = target_docs[verse+"@"+target_lang_file].split()
                                    
                                    for target_positin in target_positins:
                                        token = taget_tokens[target_positin]
                                        if token in res[target_lang]:
                                            res[target_lang][token]['count'] += 1
                                            if res[target_lang][token]['count'] < 50:
                                                res[target_lang][token]['verses'].append(doc["_id"])
                                                if target_lang_file not in res[target_lang][token]['trg_editions']:
                                                    res[target_lang][token]['trg_editions'].append(target_lang_file) 
                                        else:
                                            res[target_lang][token] = {'count':1, 'verses':[doc["_id"]], 'trg_editions':[target_lang_file]} 

        return res