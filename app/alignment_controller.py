import json
from app.document_retrieval import DocumentRetriever

from app.general_align_reader import GeneralAlignReader 

align_reader = GeneralAlignReader()
doc_retriever = DocumentRetriever()



def get_links(editions, verse_id, edition_token_offset):
    links = []
    for li1, edition1 in enumerate(editions):
        for edition2 in editions[li1+1:]:

            aligns = align_reader.get_verse_alignment([verse_id], edition1, edition2)
            print(verse_id, edition1, edition2, aligns)
            if verse_id in aligns: # TODO sometimes we don't have a verse in another lang.
                links.extend([{"source": edition_token_offset[edition1] + f, "target":edition_token_offset[edition2] + s, "value":1} for f,s in aligns[verse_id]])
    
    return links

def get_nodes(editions, source_edition, important_tokens, verse_id):
    not_found_editions = []
    nodes = []
    edition_token_offset = {}
    max_pos = 0
    token_nom = 1

    for li, edit in enumerate(editions):
        edition_token_offset[edit] = token_nom
        tokens = doc_retriever.retrieve_document(verse_id + "@" + edit).split()
        target_langs = get_rest_langs(editions, edit)
        if len(tokens) == 0:
            not_found_editions.append(align_reader.file_edition_mapping[edit])
            
        nodes.extend([{
            "id" : token_nom + i ,
            "tag": w,
            "group":li + 1,
            "source_language": align_reader.get_lang_from_edition(edit),
            "target_langs": target_langs,
            "pos": i+1,
            "bold": True if edit == source_edition and any(filter(lambda x: w.lower().startswith(x.lower()) ,important_tokens)) else False
            } for i,w in enumerate(tokens)])
        token_nom += len(tokens)
        max_pos  = max_pos if max_pos > len(tokens) else len(tokens)

    return nodes, edition_token_offset, max_pos, not_found_editions

def get_rest_langs(edits, to_remove_edit):
    res = []
    to_remove_lang = align_reader.get_lang_from_edition(to_remove_edit)

    for edit in edits:
        lang = align_reader.get_lang_from_edition(edit)
        if lang not in res and lang != to_remove_lang:
            res.append(lang)

    return res

def get_edits_label(all_edits, not_found_edits):
    edits_label = ""
    for edit in all_edits:
        if align_reader.file_edition_mapping[edit] not in not_found_edits:
            edits_label += align_reader.file_edition_mapping[edit] + ", "
    edits_label = edits_label[:-2]


    return edits_label

def get_messages(langs, verse_id):
    messages = []
    for lang in langs:
        messages.append(f"could not find verse {verse_id} for {lang}")
    
    return messages

def get_alignments_for_verse(verse_id, source_edition, all_editions, important_tokens):
    alignments = {"nodes":[], "links":[], "groups":0, "poses":0}

    if source_edition not in  all_editions:
        all_editions.append(source_edition)
    alignments["groups"] = len(all_editions)
    
    alignments["nodes"], edition_token_offset, alignments["poses"], not_found_editions = get_nodes(all_editions, source_edition, important_tokens, verse_id)
    
    alignments["links"] = get_links(all_editions, verse_id, edition_token_offset)

    messages = get_messages(not_found_editions, verse_id)
    edits_label = get_edits_label(all_editions, not_found_editions)
    alignments['label'] = f"Alignments for verse: {verse_id}. Editions in order: {edits_label}"
    
    return alignments, messages
