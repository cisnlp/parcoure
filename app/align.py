from flask import render_template, flash, redirect, jsonify
from app import app
# import sys
# sys.path.append("/Users/philipp/Dropbox/Inbox/simalign")
# import simalign
#from app.forms import LoginForm

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

# setting up alignment models
print("SETTING UP ALIGNMENT MODELS")
#aligner = simalign.SentenceAligner(model="bert", token_type="bpe")


class LoginForm(FlaskForm):
    english = StringField('Sentence A:', validators=[DataRequired()], default="")
    foreign = StringField('Sentence B:', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Align')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    alignment = None
    if form.validate_on_submit():
        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data))
        #res = aligner.get_word_aligns([form.english.data.split(" "), form.foreign.data.split(" ")])
        #print(res)
        alignment = {"e": form.english.data.split(" "),
                "f": form.foreign.data.split(" "), 
                "alignment": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))]}
        return render_template('index.html', title='SimAlign', form=form, alignment=alignment)
    return render_template('index.html', title='SimAlign', form=form, alignment=alignment)
