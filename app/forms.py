from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, FieldList, FormField, Form, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Required, Optional
from app.general_align_reader import GeneralAlignReader 


align_reader = GeneralAlignReader()

class VerseForm(Form):
    verse_id = StringField("verse_id")

class MultialignForm(FlaskForm):
    class Meta:
        csrf = False
    languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    verse = StringField('Bible keywords:', default="", render_kw={"placeholder":"type to search...", "data-url":"search", "autocomplete":"off"})
    verses = FieldList(
        FormField(VerseForm),
        min_entries=1,
        max_entries=50
    )
    submit = SubmitField('Align')

class MultAlignForm(FlaskForm):
    langs = [('en_kingjames', 'English - KingJames'), ('de_genfer', 'German - Genfer'), ('es_newworld', 'Spanish - Newworld')]
    verses = [(40001001, "40001001"), (40001002, "40001002")]
    l1 = SelectField('Editions', choices=langs)
    l2 = SelectField('Editions', choices=langs)
    l3 = SelectField('Editions', choices=langs)
    verseid = SelectField('VerseId', choices=verses)
    submit = SubmitField('Align')

class LexiconForm(FlaskForm):
    class Meta:
        csrf = False
    source_language = SelectField('Source language: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=[(x,x) for x in align_reader.all_langs])
    target_languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=[(x,x) for x in align_reader.all_langs])
    query = StringField('source word:', validators=[Required()], render_kw={"placeholder":"Enter a word to translate"})
    
    submit = SubmitField('Submit')

class statsForm(FlaskForm):
    file_path = StringField('File:', validators=[Required()], render_kw={"placeholder":"Enter a file for stats"})
    minimum = IntegerField('Min', validators=[Optional()])
    maximum = IntegerField('Max', validators=[Optional()])
    bin_size = IntegerField('Bin Size', validators=[Optional()], render_kw={"placeholder":20})
    submit = SubmitField('Submit')


class AlignForm(FlaskForm):
    english = StringField('Sentence A:', validators=[DataRequired(), Length(
        min=1, max=500, message="INPUT TOO LONG")], default="")
    foreign = StringField('Sentence B:', validators=[DataRequired(), Length(min=1, max=500, message="INPUT TOO LONG")])
    model = RadioField('Model', choices=[('bert', 'mBERT'), ('xlmr', 'XLM-R')], default="bert")
    # method = RadioField('Method', choices=[('inter', 'ArgMax'), ('itermax',
    #                                                              'IterMax'), ('mwmf', 'Match')], default="itermax")
    # recaptcha = RecaptchaField()
    submit = SubmitField('Align')
