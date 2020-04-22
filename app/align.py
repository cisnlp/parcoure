from flask import render_template, flash, redirect, jsonify
from app import app
import sys
sys.path.append("/mounts/work/philipp/simalign-demo/simalign")
#sys.path.append("/Users/Philipp/Dropbox/Inbox/simalign")
import simalign
#from app.forms import LoginForm

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError


class PLM(object):
    """docstring for PLM"""

    def __init__(self):
        super(PLM, self).__init__()
        print("SETTING UP ALIGNMENT MODELS...")
        self.aligners = {}
        self.aligners["bert"] = simalign.SentenceAligner(model="bert", token_type="bpe")
        # self.aligners["xlmr"] = simalign.SentenceAligner(model="xlmr", token_type="bpe")
        print("...Finished")


# setting up alignment models
# TODO find better place
if True:
    plm = PLM()


def convert_alignment(initial_output):
    result = []
    for elem in initial_output:
        i, j = elem.split("-")
        result.append([int(i), int(j)])
    return result


class LoginForm(FlaskForm):
    english = StringField('Sentence A:', validators=[DataRequired()], default="")
    foreign = StringField('Sentence B:', validators=[DataRequired()])
    model = RadioField('Model', choices=[('bert', 'mBERT'), ('xlmr', 'XLM-R')], default="bert")
    method = RadioField('Method', choices=[('inter', 'ArgMax'), ('itermax', 'IterMax'), ('mwmf', 'Match')], default="itermax")
    recaptcha = RecaptchaField()
    submit = SubmitField('Align')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    alignment = None
    if form.validate_on_submit():
        if True:
            res = plm.aligners[form.model.data].get_word_aligns([form.english.data.split(" "), form.foreign.data.split(" ")])
            res = convert_alignment(res[form.method.data])
            print(form.model.data)
            print(form.method.data)
            print(convert_alignment(res[form.method.data]))
            # {'mwmf': ['0-0', '1-1'], 'inter': ['0-0', '1-1'], 'itermax': ['0-0', '1-1']}
        else:
            res = [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))]
        alignment = {"e": form.english.data.split(" "),
                     "f": form.foreign.data.split(" "),
                     "alignment": res}
        return render_template('index.html', title='SimAlign', form=form, alignment=alignment)
    return render_template('index.html', title='SimAlign', form=form, alignment=alignment)
