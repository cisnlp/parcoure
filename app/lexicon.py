from app.align_reader import AlignReader
from app.document_retrieval import DocumentRetriever

align_reader = AlignReader()
doc_retriever = DocumentRetriever()


class Lexicon(object):

    def keep_only_containing_verses(self, docs, term, source_langauge):
        verses = []
        final_docs = []
        for doc in docs['hits']['hits']:
            tokens = doc["_source"]["content"].split()
            doc['termIndexes'] = [i for i,t in enumerate(tokens) if t.lower()==term.lower()]
            if len(doc['termIndexes']) > 0 and doc['_source']['language'] == source_langauge:
                verses.append(doc["_source"]["verse_id"])
                final_docs.append(doc)
        return final_docs, verses

    def get_translations(self, term, source_langauge, target_languages):
        res = {}

        docs = doc_retriever.search_documents(term + " " + source_langauge,
             all_docs=True, prefixed_search=False)
        
        docs['hits']['hits'], verses = self.keep_only_containing_verses(docs, term, source_langauge)
        
        for target_lang in target_languages:
            target_docs = doc_retriever.retrieve_multi_docs([verse + "@" + target_lang for verse in verses])
            res[target_lang] = {}

            verses_alignments = align_reader.get_verse_alignment(verses, align_reader.lang_prf_map[source_langauge], align_reader.lang_prf_map[target_lang])

            for doc in docs['hits']['hits']:
                verse = doc["_source"]["verse_id"]
                if verse in verses_alignments.keys():  #why we cannot get some alignments for some verses?
                    target_positins = [s for f,s in verses_alignments[verse] if f in doc['termIndexes']]
                
                if len(target_positins) > 0 and verse+"@"+target_lang in target_docs :
                    # taget_tokens = doc_retriever.retrieve_document(verse+"@"+target_lang).split()
                    taget_tokens = target_docs[verse+"@"+target_lang].split()
                    
                    for target_positin in target_positins:
                        token = taget_tokens[target_positin]
                        if token in res[target_lang]:
                            res[target_lang][token]['count'] += 1
                            if res[target_lang][token]['count'] < 50:
                                res[target_lang][token]['verses'].append(doc["_id"])
                        else:
                            res[target_lang][token] = {'count':1, 'verses':[doc["_id"]]}

        return res
                        

