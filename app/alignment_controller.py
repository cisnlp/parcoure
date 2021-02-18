import json
from app.document_retrieval import DocumentRetriever
from app.alignment_induceer import get_induced_alignments
from app.general_align_reader import GeneralAlignReader 


align_reader = GeneralAlignReader()
doc_retriever = DocumentRetriever()

def add_links_with_offset(links, lang_token_offset, lang1, lang2, aligns):
    links.extend([{"source": lang_token_offset[lang1] + f, "target":lang_token_offset[lang2] + s, "value":1} for f,s in aligns])

def get_induced_links(source_lang, target_lang, verse_id, lang_token_offset):
    links = []

    aligns = get_induced_alignments(source_lang, target_lang, verse_id, align_reader)
    add_links_with_offset(links, lang_token_offset, source_lang, target_lang, aligns)

    return links

def get_links(langs, verse_id, lang_token_offset):
    links = []
    for li1, lang1 in enumerate(langs):
        for lang2 in langs[li1+1:]:

            aligns = align_reader.get_verse_alignment([verse_id], lang1, lang2)
            print(verse_id, lang1, lang2, aligns)
            if verse_id in aligns: # TODO sometimes we don't have a verse in another lang.
                add_links_with_offset(links, lang_token_offset, lang1, lang2, aligns[verse_id])
    
    return links

def get_nodes(langs, source_lang, important_tokens, verse_id):
    if source_lang not in langs:
        langs.append(source_lang)

    nodes = []
    lang_token_offset = {}
    max_pos = 0
    token_nom = 1

    for li, lang in enumerate(langs):
        lang_token_offset[lang] = token_nom
        tokens = doc_retriever.retrieve_document(verse_id + "@" + lang).split()
        target_langs = get_rest_of_langs(langs, lang)
        
        nodes.extend([{
            "id" : token_nom + i ,
            "tag": w,
            "group":li + 1,
            "source_language": lang,
            "target_langs": target_langs,
            "pos": i+1,
            "bold": True if lang == source_lang and any(filter(lambda x: w.lower().startswith(x.lower()) ,important_tokens)) else False
            } for i,w in enumerate(tokens)])
        token_nom += len(tokens)
        max_pos  = max_pos if max_pos > len(tokens) else len(tokens)

    return nodes, lang_token_offset, max_pos

def get_rest_of_langs(langs, to_remove_lang):
    res = langs[:]
    res.remove(to_remove_lang)  
    return res

def get_alignments_for_verse(verse_id, source_language, all_langs, important_tokens):
    alignments = {"nodes":[], "links":[], "groups":0, "poses":0}

    if source_language not in  all_langs:
        all_langs.append(source_language)
    alignments["groups"] = len(all_langs)
    
    alignments["nodes"], lang_token_offset, alignments["poses"] = get_nodes(all_langs, source_language, important_tokens, verse_id)
    
    alignments["links"] = get_links(all_langs, verse_id, lang_token_offset)

    return alignments

def induce_alingment(verse_id, source_lang, target_lang, important_tokens):
    alignments = {"nodes":[], "links":[], "groups":2, "poses":0}

    alignments["nodes"], lang_token_offset, alignments["poses"] = get_nodes([target_lang], source_lang, important_tokens, verse_id)

    alignments["links"] = get_induced_links(source_lang, target_lang, verse_id, lang_token_offset)

    return alignments