from flask import render_template, request
from app import app, models, utils
from app.forms import *
from flask_restful import reqparse
import json
import requests
import os
from app.document_retrieval import DocumentRetriever
from app.lexicon import Lexicon
import app.controler as controler
import app.alignment_controller as alignment_controler
from app.stats import one_lang_stat_vals, two_langs_stat_vals, one_edition_stat_vals, two_edition_stat_vals, no_lang_stat_vals

# setting up alignment models
if utils.CIS:
    plm = models.PLM()

parser = reqparse.RequestParser()
doc_retriever = DocumentRetriever()
lexicon = Lexicon()

def convert_alignment(initial_output):
    processed_output = {}
    for method, data in initial_output.items():
        result = []
        for elem in data:
            i, j = elem.split("-")
            result.append([int(i), int(j)])
        processed_output[method] = result
    return processed_output

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/multalign', methods=['GET', 'POST'])
def multalign():
    print("man", utils.config_dir)
    form = MultialignForm()
    alignment = None
    prev_verses = {}
    if form.validate_on_submit():

        doc_alignments = []
        all_messages = []
        errorA = None
        utils.LOG.info("Received: {} ||| {} ".format(form.languages.data, ("_".join([x.verse_id.data for x in form.verses]) + str(len(form.verses)))))
        documents = [x.verse_id.data.strip() for x in form.verses]
        documents = list(filter(lambda x: len(x.split('@')) > 1, documents)) 
        input_tokens = form.verse.data.strip().split()
        
        if len(documents) == 0:
            errorA = 'Please select at least one bible verse.'
        else:

            for document in documents: 
                if document not in prev_verses: # the user may select a verse twice
                    verse_id, source_file = (document.split('@')[0], document.split('@')[1])

                    alignments, messages = alignment_controler.get_alignments_for_verse(verse_id, source_file, form.languages.data[:], input_tokens)
                    doc_alignments.append(alignments)
                    all_messages.extend(messages)
                    prev_verses[document] = "<span style=\"color: blue;\">" +  align_reader.file_edition_mapping[source_file] + "</span>: " 
                    prev_verses[document] += " ".join([x["tag"] for x in alignments["nodes"] if x["group"] == alignments["groups"]]) 

        return render_template('multalign.html', title='ParCourE', form=form,
         docs_alignment=doc_alignments, doc_count=len(doc_alignments), prev_verses=prev_verses, messages=all_messages,
          errorA=errorA, errorB=None, corpus=utils.corpus_name)
        
    else:
        errorA = None
        errorB = None
        for error in form.errors:
            if error == "verse":
                errorA = form.errors['verse'][0]
            if error == "languages":
                errorB = form.errors['languages'][0]
        utils.LOG.info("Input error: {}".format(form.errors))
        utils.LOG.info("Running index finished.")
        return render_template('multalign.html', title='ParCourE', form=form, alignment=alignment,
         errorA=errorA, errorB=errorB, corpus=utils.corpus_name)
    utils.LOG.info("Running index finished.")
    return render_template('multalign.html', title='ParCourE', form=form, alignment=alignment,
     errorA=None, errorB=None, corpus=utils.corpus_name)

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
# def index():
#     utils.LOG.info("Running index ...") 
#     form = AlignForm()
#     alignment = None
#     if form.validate_on_submit():
#         utils.LOG.info("Received: {} ||| {}".format(form.english.data, form.foreign.data))
#         if utils.CIS:
#             res = plm.aligners[form.model.data].get_word_aligns(
#                 [form.english.data.split(" "), form.foreign.data.split(" ")])
#             res = convert_alignment(res)
#         else:
#             res = {"inter": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))],
#                     "itermax": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))],
#                     "mwmf": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))]}
#         alignment = {"e": form.english.data.split(" "),
#                     "f": form.foreign.data.split(" "),
#                     "alignment": res}
#         utils.LOG.info("Sent: {}".format(alignment))
#         utils.LOG.info("Running index finished.")
#         return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)
#     else:
#         errorA = None
#         errorB = None
#         for error in form.errors:
#             if error == "english":
#                 errorA = True
#             if error == "foreign":
#                 errorB = True
#         utils.LOG.info("Input error: {}".format(form.errors))
#         utils.LOG.info("Running index finished.")
#         return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=errorA, errorB=errorB)
#     utils.LOG.info("Running index finished.")
#     return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)

@app.route('/search', methods=['GET'])
def search():
    print("Call for GET /search")
    parser.add_argument('q')
    query_string = parser.parse_args()
    q = query_string['q'].strip()

    language_files = ""
    verse_id = -1
    while q[:2] == "l:" or q[:2] == "L:" or q[:2] == "v:" or q[:2] == "V:":
        if q[:2] == "l:" or q[:2] == "L:":
            q = q[2:]

            tokens = q.split(' ')
            if len(tokens[0]) > 2:
                for edition in align_reader.edition_file_mapping:
                    if edition.startswith(tokens[0]):
                        language_files = align_reader.edition_file_mapping[edition]
                        break
            tokens.pop(0)
            q = "  ".join(tokens)
        else:
            q = q[2:]
            tokens = q.split(' ')
            try:
                verse_id = int(tokens[0])
                verse_id = str(verse_id)
            except Exception as e:
                print(e)
                pass
            print(verse_id)
            tokens.pop(0)
            q = " ".join(tokens)
            
    if len(q) == 0 and verse_id == -1 :
        return app.response_class(
        response="",
        status=200,
        mimetype='application/json'
    )

    utils.LOG.info("searching for: query: {}, langs: {}, verse: {}".format(q,language_files, verse_id))
    if len(q.split()) <= 1: #or len(q) < 10:
        data = doc_retriever.search_documents(q + " " + language_files, verse=None if verse_id==-1 else verse_id, doc_count=50, prefixed_search=True)
    else:
        data = doc_retriever.search_documents(q + " " + language_files, verse=None if verse_id==-1 else verse_id, doc_count=50, prefixed_search=False)
    utils.LOG.info(data)
    beers = []
    i = 1
    for hit in data['hits']['hits']:
        beer = {}
        beer["value"] = hit["_id"]
        i += 1
        beer["text"] = "<span style=\"color: blue;\">" + align_reader.file_edition_mapping[hit["_source"]["language"]] + "</span>: " + hit["_source"]["content"]
        beers.append(beer)
    
    response = app.response_class(
        response=json.dumps(beers),
        status=200,
        mimetype='application/json'
    )
    return response

def convert_to_view_jason(translations, source_lang, source_word):
    # print(translations)
    res = {}
    for trg_lang, words in translations.items():
        res[trg_lang] = {}
        res[trg_lang]["source_lang"] = source_lang
        res[trg_lang]["l_name"] = trg_lang
        res[trg_lang]["children"] = []

        if len(words) == 0:
            words['*no translation*'] = {'count':-1, 'verses':[], 'trg_editions':[], }
        tot = sum([x['count'] for x in words.values()])

        for word,data in words.items():
            if data['count']/tot > 0.05:
                res[trg_lang]["children"].append({"label":word, "value":data['count']/tot, "verses":data['verses'], "target_language": data['trg_editions'], 'source_word': source_word, "count":data['count']})
    return res

@app.route('/lexicon', methods=['GET', 'POST'])
def dictionary():
    form = LexiconForm()
    res = None
    utils.LOG.info("Received: {} ||| {} ||| {}".format(form.target_languages.data, form.query.data, form.source_language.data))

    if form.validate_on_submit():
        res = {}
        query = form.query.data
        target_langs = form.target_languages.data
        query_terms = query.strip().split(' ')
        source_language = form.source_language.data

        for query_term in query_terms:
            translations = lexicon.get_translations(query_term, source_language, target_langs)
            res[query_term] = convert_to_view_jason(translations, source_language, query_term)
            
    else:
        errorA = None
        errorB = None
        errorC = None
        for error in form.errors:
            if error == "source_language":
                errorA = form.errors['source_language'][0]
            if error == "query":
                errorC = form.errors['query'][0]
            if error == "target_languages":
                errorB = form.errors['target_languages'][0]
        utils.LOG.info("Input error: {}".format(form.errors))
        utils.LOG.info("1 Running lexicon finished.")
        return render_template('lexicon.html', title='ParCourE', form=form, dictionary=res, errorA=errorA, errorB=errorB, errorC=errorC)
    utils.LOG.info("2 Running lexicon finished.")

    return render_template('lexicon.html', title='ParCourE', form=form, dictionary=res, errorA=None, errorB=None, errorC=None)

def checkForErrorInInput(stat_type, lang1, lang2, lang_file1, lang_file2):
    if stat_type in two_langs_stat_vals:
        if lang1 not in align_reader.all_langs or lang2 not in align_reader.all_langs:
            return 'you should select two languages for this stat'
    elif stat_type in two_edition_stat_vals:
        if lang_file1 not in align_reader.file_edition_mapping.keys() or lang_file2 not in align_reader.file_edition_mapping.keys():
            return 'you should select two editions for this stat'
    elif stat_type in one_lang_stat_vals:
        if lang1 not in align_reader.all_langs:
            return 'you should select one languages for this stat'
    elif stat_type in one_edition_stat_vals:
        if lang_file1 not in align_reader.file_edition_mapping.keys():
            return 'you should select one editions for this stat'

@app.route('/stats', methods=['GET', 'POST'])
def statitics():
    errorA = None
    form = statsForm()
    res = None
    utils.LOG.info("Received: {} ||| {} ||| {} ||| {} ||| {} ||| {} ||| {} ||| {}".format(form.stat_type.data, form.lang1.data, form.lang2.data, form.edition_1.data, form.edition_2.data, form.minimum.data, form.maximum.data, form.bin_count.data))
    
    if form.validate_on_submit():
        res = []
        stat_type = form.stat_type.data 
        lang1 = form.lang1.data
        lang2 = form.lang2.data
        lang_file_1 = form.edition_1.data
        lang_file2 = form.edition_2.data
        min = form.minimum.data
        max = form.maximum.data
        bin_count = 20 if form.bin_count.data == None or form.bin_count.data < 1 else form.bin_count.data
        
        errorA = checkForErrorInInput(stat_type, lang1, lang2, lang_file_1, lang_file2)
        if errorA == None:
            res = controler.extract_data_from_file(stat_type, lang1, lang2, lang_file_1, lang_file2, bin_count, min, max)
    else:
        print("sag")

    return render_template('stats.html', title='ParCourE-stats', form=form, stats=res, errorA=errorA)

@app.route('/information', methods=['GET', 'POST'])
def information():
    info = []

    #info_obj ={}
    #info_obj['title'] = 'Impressum'
    #info_obj['message'] = 'This tool was created at <a href="https://www.cis.uni-muenchen.de/funktionen/impressum/index.html">CIS - LMU Munich</a>.'
    #info_obj['link'] = 'https://www.cis.uni-muenchen.de/funktionen/impressum/index.html'
    #info.append(info_obj)
    
    info_obj ={}
    info_obj['title'] = 'Language Codes'
    info_obj['message'] = 'We are using iso639-3. To see a list of language names and their corresponding codes see the link below.'
    info_obj['link'] = 'https://iso639-3.sil.org/code_tables/639/data'
    info.append(info_obj)

    info_obj ={}
    info_obj['title'] = 'SimAlign'
    info_obj['message'] = 'If you slect a edition pair both from the following list, they will be aligned by Simalign'
    info_obj['link'] = 'https://simalign.cis.lmu.de/'
    info_obj['table'] = [align_reader.file_edition_mapping[x] for x in align_reader.bert_files]
    info.append(info_obj)

    info_obj ={}
    info_obj['title'] = 'Eflomal'
    info_obj['message'] = 'If at least one of you selected editions comes from the following list, the alignment would be from eflomal'
    info_obj['link'] = 'https://github.com/robertostling/eflomal'
    info_obj['table'] = [y for (x,y) in align_reader.file_edition_mapping.items() if x not in align_reader.bert_files]
    info.append(info_obj)

    for info_obj in info:
        if 'table' in info_obj:
            info_obj['len'] = len(info_obj['table'])
    
    return render_template('information.html', title='Information', info=info)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r