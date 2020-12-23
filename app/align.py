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


@app.route('/multalign', methods=['GET', 'POST'])
def multalign():
    form = MultialignForm()
    alignment = None
    if form.validate_on_submit():
        doc_alignments = []
        errorA = None
        utils.LOG.info("Received: {} ||| {} ".format(form.languages.data, ("_".join([x.verse_id.data for x in form.verses]) + str(len(form.verses)) + "_" + str(form.verses[0].verse_id) )))
        documents = [x.verse_id.data.strip() for x in form.verses]
        
        documents = list(filter(lambda x: len(x.split('@')) > 1, documents))
        input_tokens = form.verse.data.strip().split()
        
        if len(documents) == 0:
            errorA = 'Please select at least one bible verse.'
        else:
            for document in documents:
                verse_id, source_language = (document.split('@')[0], document.split('@')[1])

                alignments = alignment_controler.get_alignments_for_verse(verse_id, source_language, form.languages.data[:], input_tokens)
                doc_alignments.append(alignments)

        return render_template('multalign.html', title='SimAlign', form=form, docs_alignment=doc_alignments, doc_count=len(doc_alignments), errorA=errorA, errorB=None)
        
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
        return render_template('multalign.html', title='SimAlign', form=form, alignment=alignment, errorA=errorA, errorB=errorB)
    utils.LOG.info("Running index finished.")
    return render_template('multalign.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    utils.LOG.info("Running index ...") 
    form = AlignForm()
    alignment = None
    if form.validate_on_submit():
        utils.LOG.info("Received: {} ||| {}".format(form.english.data, form.foreign.data))
        if utils.CIS:
            res = plm.aligners[form.model.data].get_word_aligns(
                [form.english.data.split(" "), form.foreign.data.split(" ")])
            res = convert_alignment(res)
            # print(form.model.data)
            # print(form.method.data)
            # print(res)
            # {'mwmf': ['0-0', '1-1'], 'inter': ['0-0', '1-1'], 'itermax': ['0-0', '1-1']}
        else:
            res = {"inter": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))],
                    "itermax": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))],
                    "mwmf": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))]}
        alignment = {"e": form.english.data.split(" "),
                    "f": form.foreign.data.split(" "),
                    "alignment": res}
        utils.LOG.info("Sent: {}".format(alignment))
        utils.LOG.info("Running index finished.")
        return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)
    else:
        errorA = None
        errorB = None
        for error in form.errors:
            if error == "english":
                errorA = True
            if error == "foreign":
                errorB = True
        utils.LOG.info("Input error: {}".format(form.errors))
        utils.LOG.info("Running index finished.")
        return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=errorA, errorB=errorB)
    utils.LOG.info("Running index finished.")
    return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)

@app.route('/search', methods=['GET'])
def search():
    print("Call for GET /search")
    parser.add_argument('q')
    query_string = parser.parse_args()
    q = query_string['q'].strip()

    languages = ""
    verse_id = -1
    while q[:2] == "l:" or q[:2] == "L:" or q[:2] == "v:" or q[:2] == "V:":
        if q[:2] == "l:" or q[:2] == "L:":
            q = q[2:]

            tokens = q.split(' ')
            if len(tokens[0]) > 2:
                for edition in align_reader.lang_name_file_mapping:
                    if edition.startswith(tokens[0]):
                        languages = align_reader.lang_name_file_mapping[edition]
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

    utils.LOG.info("searching for: query: {}, langs: {}, verse: {}".format(q,languages, verse_id))
    data = doc_retriever.search_documents(q + " " + languages, verse=None if verse_id==-1 else verse_id)
    utils.LOG.info(data)
    beers = []
    i = 1
    for hit in data['hits']['hits']:
        beer = {}
        beer["value"] = hit["_id"]
        i += 1
        beer["text"] = "<span style=\"color: blue;\">" + align_reader.file_lang_name_mapping[hit["_source"]["language"]] + "</span>: " + hit["_source"]["content"]
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
        # res[lang]["l_name"] = align_reader.file_lang_name_mapping[lang]
        res[trg_lang]["l_name"] = trg_lang
        res[trg_lang]["children"] = []
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
        return render_template('lexicon.html', title='SimAlign', form=form, dictionary=res, errorA=errorA, errorB=errorB, errorC=errorC)
    utils.LOG.info("2 Running lexicon finished.")

    return render_template('lexicon.html', title='SimAlign', form=form, dictionary=res, errorA=None, errorB=None, errorC=None)


@app.route('/stats', methods=['GET', 'POST'])
def stats():
    form = statsForm()
    res = None
    utils.LOG.info("Received: {} ||| {} ||| {} ||| {}".format(form.file_path.data, form.minimum.data, form.maximum.data, form.bin_size.data))
    
    if form.validate_on_submit():
        res = []
        f_path = form.file_path.data
        min = form.minimum.data
        max = form.maximum.data
        bin_size = 20 if form.bin_size.data == None or form.bin_size.data < 1 else form.bin_size.data
        if not os.path.exists(f_path):
            errorA = "Bad file path!"
        else:
            res = controler.extract_data_from_file(f_path, bin_size, min, max)
    else:
        print("sag")
    #     query = form.query.data
    #     target_langs = form.target_languages.data
    #     query_terms = query.strip().split(' ')
    #     source_language = form.source_language.data

    #     for query_term in query_terms:
    #         translations = lexicon.get_translations(query_term, source_language, target_langs)
    #         res[query_term] = convert_to_view_jason(translations, source_language, query_term)
            
    # else:
    #     errorA = None
    #     errorB = None
    #     errorC = None
    #     for error in form.errors:
    #         if error == "source_language":
    #             errorA = form.errors['source_language'][0]
    #         if error == "query":
    #             errorC = form.errors['query'][0]
    #         if error == "target_languages":
    #             errorB = form.errors['target_languages'][0]
    #     utils.LOG.info("Input error: {}".format(form.errors))
    #     utils.LOG.info("1 Running lexicon finished.")
    #     return render_template('lexicon.html', title='SimAlign', form=form, dictionary=res, errorA=errorA, errorB=errorB, errorC=errorC)
    # utils.LOG.info("2 Running lexicon finished.")

    return render_template('stats.html', title='SimAlign-Demo-stats', form=form, stats=res, errorA=None)


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