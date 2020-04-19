from flask import render_template, flash, redirect, jsonify
from app import app
#from app.forms import LoginForm

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    english = StringField('English', validators=[DataRequired()])
    foreign = StringField('Foreign', validators=[DataRequired()])
    submit = SubmitField('Align')


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)


@app.route("/data")
def data():
    return jsonify({"text": "an example text", "foreign": "another text", "alignment": 5.6})


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    alignment = None
    if form.validate_on_submit():
        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data))
        print(form.english.data)
        print(form.foreign.data)
        alignment = form.english.data + "|||" + form.foreign.data
        return render_template('login.html', title='Sign In', form=form, alignment=alignment, mydata=int(form.english.data))
    return render_template('login.html', title='Sign In', form=form, alignment=alignment, mydata=10.0)
