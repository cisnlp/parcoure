from flask import render_template, request
from app import app, models, utils
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length


# setting up alignment models
if utils.CIS:
    plm = models.PLM()


def convert_alignment(initial_output):
    processed_output = {}
    for method, data in initial_output.items():
        result = []
        for elem in initial_output:
            i, j = elem.split("-")
            result.append([int(i), int(j)])
        processed_output[method] = result
    return processed_output


class LoginForm(FlaskForm):
    english = StringField('Sentence A:', validators=[DataRequired(), Length(
        min=1, max=500, message="INPUT TOO LONG")], default="")
    foreign = StringField('Sentence B:', validators=[DataRequired(), Length(min=1, max=500, message="INPUT TOO LONG")])
    model = RadioField('Model', choices=[('bert', 'mBERT'), ('xlmr', 'XLM-R')], default="bert")
    # method = RadioField('Method', choices=[('inter', 'ArgMax'), ('itermax',
    #                                                              'IterMax'), ('mwmf', 'Match')], default="itermax")
    recaptcha = RecaptchaField()
    submit = SubmitField('Align')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    utils.LOG.info("Running index ...")
    form = LoginForm()
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
