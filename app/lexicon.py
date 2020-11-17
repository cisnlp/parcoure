from app.align_reader import AlignReader

align_reader = AlignReader()


class Lexicon(object):

    def get_translations(self, query, target_languages):
        docs = docRetriever.get_documents(query_term + " " + align_reader.lang_name_file_mapping[source_language],
             all_docs=True, prefixed_search=False)
            
        print(query_term, "retrieved doc count: ", len(docs['hits']['hits']))
        for language in target_langs:
            for 