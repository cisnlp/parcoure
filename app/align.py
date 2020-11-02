from flask import render_template, request
from app import app, models, utils
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, RadioField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Required
from app.align_reader import AlignReader 
from flask_restful import reqparse
import json
import requests
import os


# setting up alignment models
if utils.CIS:
    plm = models.PLM()

align_reader = AlignReader()
parser = reqparse.RequestParser()

def convert_alignment(initial_output):
    processed_output = {}
    for method, data in initial_output.items():
        result = []
        for elem in data:
            i, j = elem.split("-")
            result.append([int(i), int(j)])
        processed_output[method] = result
    return processed_output


class LoginForm(FlaskForm):
    # languages = SelectMultipleField('Target languages: ', choices=alignReader.all_langs)
    languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    verse = SelectField('Bible keywords:', coerce=str, validate_choice=False, default="", render_kw={"placeholder":"type to search...", "data-url":"search", "autocomplete":"off"})
    # foreign = StringField('Sentence B:', validators=[DataRequired(), Length(min=1, max=500, message="INPUT TOO LONG")])
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # os.remove("../static/files/alignments")
    utils.LOG.info("Running index ...")
    form = LoginForm()
    alignment = None

    if form.validate_on_submit():
        errorA = None
        alignments = {"nodes":[], "links":[], "groups":0, "poses":0}
        utils.LOG.info("Received: {} ||| {} ||| {}".format(form.languages.data, form.verse.data, type(form.verse.data)))
        if form.verse.data.strip() == '':
            errorA = 'This field is required.'
        elif len(form.verse.data.strip().split('@')) != 2:
            errorA = 'Please select a valid Bible verse.'
        else:
            
            verse_id, source_language = (form.verse.data.strip().split('@')[0], form.verse.data.strip().split('@')[1])
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
                tokens = align_reader.get_text_for_lang(lang1)[verse_id].split() 
                alignments["nodes"].extend([{"id" : token_nom + i , "tag": w, "group":li + 1, "pos": i+1} for i,w in enumerate(tokens)])
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
            # with open("../static/files/alignments", 'w') as file:
            #     file.write(json.dumps(alignments))
        # if utils.CIS:
        #     res = plm.aligners[form.model.data].get_word_aligns(
        #         [form.english.data.split(" "), form.foreign.data.split(" ")])
        #     res = convert_alignment(res)
        #     # print(form.model.data)
        #     # print(form.method.data)
        #     # print(res)
        #     # {'mwmf': ['0-0', '1-1'], 'inter': ['0-0', '1-1'], 'itermax': ['0-0', '1-1']}
        # else:
        #     res = {"inter": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))],
        #            "itermax": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))],
        #            "mwmf": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))]}
        # alignment = {"e": form.english.data.split(" "),
        #              "f": form.foreign.data.split(" "),
        #              "alignment": res}
        # utils.LOG.info("Sent: {}".format(alignment))
        # utils.LOG.info("Running index finished.")
        return render_template('index.html', title='SimAlign', form=form, alignment=alignment, errorA=errorA, errorB=None)
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
        return

    ealstic_url = utils.es_index_url + '/_search'

    
    query = {
        "query": {
            "bool":{
                "should": {
                    "multi_match": {
                        "fields": ["content", "language"],
                        "query": q + " " + languages ,
                        "type": "cross_fields"#,
                        # "use_dis_max": False
                        # , "analyzer":"autocomplete"
                    }
                }
            }
        },
        "size": 10
    }

    if verse_id != -1:
        query["query"]["bool"]["filter"]  = {"match": { "verse_id" : verse_id }}

    print(query)
    resp = requests.get(ealstic_url, data=json.dumps(query), headers = {'Content-Type': 'application/json'})
    data = resp.json()
    
    print(data)
    beers = []
    i = 1
    for hit in data['hits']['hits']:
        beer = {}
        beer["value"] = hit["_id"]
        i += 1
        beer["text"] = hit["_source"]["content"]
        beers.append(beer)
    
    response = app.response_class(
        response=json.dumps(beers),
        status=200,
        mimetype='application/json'
    )
    return response


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