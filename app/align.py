from flask import render_template, request
from app import app, models, utils
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, RadioField, SelectField, SelectMultipleField, FieldList, FormField, Form
from wtforms.validators import DataRequired, Length, Required
from app.align_reader import AlignReader 
from flask_restful import reqparse
import json
import requests
import os
from app.document_retrieval import DocumentRetriever
from app.lexicon import Lexicon


# setting up alignment models
if utils.CIS:
    plm = models.PLM()

align_reader = AlignReader()
parser = reqparse.RequestParser()
docRetriever = DocumentRetriever()
Lexicon = Lexicon()

def convert_alignment(initial_output):
    processed_output = {}
    for method, data in initial_output.items():
        result = []
        for elem in data:
            i, j = elem.split("-")
            result.append([int(i), int(j)])
        processed_output[method] = result
    return processed_output

class VerseForm(Form):
    verse_id = StringField("verse_id")

class LoginForm(FlaskForm):
    # languages = SelectMultipleField('Target languages: ', choices=alignReader.all_langs)
    languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    verse = StringField('Bible keywords:', default="", render_kw={"placeholder":"type to search...", "data-url":"search", "autocomplete":"off"})
    # verse = StringField('Sentence B:', render_kw={"placeholder":"type to search...", "data-url":"search", "autocomplete":"off"})
    verses = FieldList(
        FormField(VerseForm),
        min_entries=1,
        max_entries=20
    )
    # model = RadioField('Model', choices=[('bert', 'mBERT'), ('xlmr', 'XLM-R')], default="bert")
    # method = RadioField('Method', choices=[('inter', 'ArgMax'), ('itermax',
    #                                                              'IterMax'), ('mwmf', 'Match')], default="itermax")
    # recaptcha = RecaptchaField()
    submit = SubmitField('Align')


class MultAlignForm(FlaskForm):
    langs = [('en_kingjames', 'English - KingJames'), ('de_genfer', 'German - Genfer'), ('es_newworld', 'Spanish - Newworld')]
    verses = [(40001001, "40001001"), (40001002, "40001002")]
    l1 = SelectField('Editions', choices=langs)
    l2 = SelectField('Editions', choices=langs)
    l3 = SelectField('Editions', choices=langs)
    verseid = SelectField('VerseId', choices=verses)
    submit = SubmitField('Align')

def retrieve_document(document):
    ealstic_url = utils.es_index_url + '/_doc/' + document 
    resp = requests.get(ealstic_url, headers = {'Content-Type': 'application/json'})
    data = resp.json()
    if data["found"] == True:
        return data["_source"]["content"]
    else:
        print("error", "counld not retrieve the document from elastic searcch", document)
        return ""
    

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    alignment = None

    if form.validate_on_submit():
        doc_alignments = []
        errorA = None
        utils.LOG.info("Received: {} ||| {} ".format(form.languages.data, ("_".join([x.verse_id.data for x in form.verses]) + str(len(form.verses)) + "_" + str(form.verses[0].verse_id) )))
        documents = [x.verse_id.data.strip() for x in form.verses]
        print(documents)
        documents = list(filter(lambda x: len(x.split('@')) > 1, documents))
        input_tokens = form.verse.data.strip().split()
        print(documents)
        if len(documents) == 0:
            errorA = 'Please select at least one bible verse.'
        else:
            for document in documents:
                alignments = {"nodes":[], "links":[], "groups":0, "poses":0}
                verse_id, source_language = (document.split('@')[0], document.split('@')[1])
                print(verse_id, source_language)
                all_langs = form.languages.data
                if source_language not in  all_langs:
                    all_langs.append(source_language)
                
                lang_token_offset = {}
                token_nom = 1
                alignments["groups"] = len(all_langs)
                for li in range(len(all_langs)):
                    lang1 = all_langs[li]
                    lang_token_offset[lang1] = token_nom
                    tokens = retrieve_document(verse_id + "@" + lang1).split()
                    alignments["nodes"].extend([{
                        "id" : token_nom + i ,
                        "tag": w,
                        "group":li + 1,
                        "pos": i+1,
                        "bold": True if lang1 == source_language and any(filter(lambda x: w.lower().startswith(x.lower()) ,input_tokens)) else False
                        } for i,w in enumerate(tokens)])
                    token_nom += len(tokens)
                    alignments["poses"]  = alignments["poses"] if alignments["poses"] > len(tokens) else len(tokens)
                    
                for li in range(len(all_langs)):
                    lang1 = all_langs[li]
                    for li2 in range(li+1,len(all_langs)):
                        lang2 = all_langs[li2]
                        aligns = align_reader.get_verse_alignment([verse_id], align_reader.lang_prf_map[lang1], align_reader.lang_prf_map[lang2])
                        alignments["links"].extend([{"source": lang_token_offset[lang1] + f, "target":lang_token_offset[lang2] + s, "value":1} for f,s in aligns[verse_id]])
                print(json.dumps(alignments))
                alignment = json.dumps(alignments)
                doc_alignments.append(alignment)


        return render_template('index.html', title='SimAlign', form=form, docs_alignment=doc_alignments, doc_count=len(doc_alignments), errorA=errorA, errorB=None)
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
        return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=errorA, errorB=errorB)
    utils.LOG.info("Running index finished.")
    return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)


@app.route('/multalign', methods=['GET', 'POST'])
def multalign():
    utils.LOG.info("Building multalign.")
    form = MultAlignForm()
    return render_template('multalign.html', title='SimAlign', form=form, errorA=None, errorB=None)


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
            if len(tokens) > 1 and tokens[0].lower() + " " + tokens[1].lower() in align_reader.lang_name_file_mapping:
                languages += align_reader.lang_name_file_mapping[tokens[0].lower() + " " + tokens[1].lower()] + " "
                tokens.pop(0)
            elif tokens[0].lower() in align_reader.lang_name_file_mapping:
                languages += align_reader.lang_name_file_mapping[tokens[0].lower()] + " "
            else:
                # unknown language, we neglect it
                pass
            tokens.pop(0)
            q = "  ".join(tokens)
        else:
            q = q[2:]
            tokens = q.split(' ')
            print(tokens)
            try:
                verse_id = int(tokens[0])
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

    data = docRetriever.get_documents(q + " " + languages, verse=None if verse_id==-1 else verse_id)
    print(data)
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

class LexiconForm(FlaskForm):
    source_language = SelectField('Source language: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    target_languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    # query = StringField('Bible keywords:', default="", render_kw={"placeholder":"type to search...", "data-url":"search", "autocomplete":"off"})
    query = StringField('source word:', default="", render_kw={"placeholder":"Enter a word to translate"})
    
    submit = SubmitField('Translate')

@app.route('/lexicon', methods=['GET', 'POST'])
def lexicon():
    form = LexiconForm()
    alignment = None
    

    utils.LOG.info("Received: {} ||| {} ||| {}".format(form.target_languages.data, form.query.data, form.source_language.data))

    if form.validate_on_submit():
        query = form.query.data
        target_langs = form.target_languages
        query_terms = query.split(' ')
        source_language = form.source_language.data


        for query_term in query_terms:
            lexicon.get_translations(query_term, source_language, target_langs)
            
    else:
        errorA = None
        errorB = None
        for error in form.errors:
            if error == "query":
                errorA = form.errors['query'][0]
            if error == "languages":
                errorB = form.errors['languages'][0]
        utils.LOG.info("Input error: {}".format(form.errors))
        utils.LOG.info("1 Running lexicon finished.")
        return render_template('lexicon.html', title='SimAlign', form=form, alignment=alignment, errorA=errorA, errorB=errorB)
    utils.LOG.info("2 Running lexicon finished.")

    return render_template('lexicon.html', title='SimAlign', form=form, alignment=alignment, errorA=None, errorB=None)


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