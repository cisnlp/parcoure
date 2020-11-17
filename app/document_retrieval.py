from app import utils
import requests
import json

class DocumentRetriever(object):

    def __init__(self):
        self.ealstic_url_autocomplete = utils.es_index_url + '/_search'
        self.ealstic_url_normal = utils.es_index_url_noedge + '/_search'

    def get_documents(self, q, verse=None, all_docs=False, doc_count=10, prefixed_search=True):
        """
        since elasticsearch doesn't support more that 10000 hits per run we currently 
        stick to at most 10000 retrieved docs,
        we can later implement retrieval of all matched docs
        """
        query = {
            "query": {
                "bool":{
                    "should": {
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
        query["size"] = 10000 if all_docs == True or doc_count > 10000 else doc_count

        if verse != None:
            query["query"]["bool"]["filter"]  = {"match": { "verse_id" : verse }}

        print(query)
        resp = requests.get(
            self.ealstic_url_autocomplete if prefixed_search else self.ealstic_url_normal, 
            data=json.dumps(query), headers = {'Content-Type': 'application/json'})
        return resp.json()