from app import utils
import requests
import json
from app.utils import LOG

class DocumentRetriever(object):

    def __init__(self):
        self.ealstic_search_autocomplete_url = utils.es_index_url + '/_search'
        self.ealstic_search_normal_url = utils.es_index_url_noedge + '/_search'
        self.elastic_doc_url = utils.es_index_url + '/_doc/'
        self.elastic_docs_url = utils.es_index_url + '/_mget/'

    def search_documents(self, q, verse=None, all_docs=False, doc_count=10, prefixed_search=True):
        """
        since elasticsearch doesn't support more that 10000 hits per run we currently 
        stick to at most 10000 retrieved docs,
        we can later implement retrieval of all matched docs
        """
        if q.strip() != "":
            query = {
                "query": {
                    "bool":{
                        "must": {
                            "multi_match": {
                                "fields": ["content", "language"],
                                "query": q ,
                                "type": "cross_fields"#,
                                # "use_dis_max": False
                                # , "analyzer":"autocomplete"
                            }
                        }
                    }
                }
            }

            if verse != None:
                query["query"]["bool"]["filter"]  = {"match": { "verse_id" : verse }}
        else:
            query = {
                "query": {
                    "bool":{
                        "must": {
                            "match": { "verse_id" : verse }
                        }
                    }
                }
            }

        query["size"] = 10000 if all_docs == True or doc_count > 10000 else doc_count


        LOG.info(query)
        resp = requests.get(
            self.ealstic_search_autocomplete_url if prefixed_search else self.ealstic_search_normal_url, 
            data=json.dumps(query), headers = {'Content-Type': 'application/json'})
        return resp.json()

    def retrieve_document(self, document):
        ealstic_url = self.elastic_doc_url + document 
        resp = requests.get(ealstic_url, headers = {'Content-Type': 'application/json'})
        data = resp.json()
        if data["found"] == True:
            return data["_source"]["content"]
        else:
            print("error", "counld not retrieve the document from elastic searcch", document)
            return ""
    
    def retrieve_multi_docs(self, docs):
        ealstic_url = self.elastic_docs_url 
        req = {"ids" : docs} 
        resp = requests.get(ealstic_url, headers = {'Content-Type': 'application/json'}, data=json.dumps(req))
        data = resp.json()
        res = {}

        if 'docs' in data:
            for d in data['docs']:
                if d['found']:  # TODO why we cannot find some documents in one language?
                    res[d["_id"]] = d["_source"]["content"] 
                else:
                    print(d)
        return res