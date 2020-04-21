from flask import render_template, flash, redirect, jsonify
from app import app
#from app.forms import LoginForm

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class LoginForm(FlaskForm):
    english = StringField('Sentence A', validators=[DataRequired()], default="")
    foreign = StringField('Sentence B', validators=[DataRequired()])
    submit = SubmitField('Align')


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)


@app.route("/data")
def data():
    return jsonify({"e": ["Das", "ist", "ein", "Beispiel", "."], 
             "f": ["WWW", "is", "an", "example", "."], 
             "alignment": [[0,1], [1,1], [3,2]]})


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    alignment = None
    if form.validate_on_submit():
        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data))
        alignment = {"e": form.english.data.split(" "),
                "f": form.foreign.data.split(" "), 
                "alignment": [[i, i] for i in range(min(len(form.english.data.split(" ")), len(form.foreign.data.split(" "))))]}
        return render_template('login.html', title='Sign In', form=form, alignment=alignment)
    return render_template('login.html', title='Sign In', form=form, alignment=alignment)
