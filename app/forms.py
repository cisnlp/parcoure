from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, RadioField, SelectField, SelectMultipleField, FieldList, FormField, Form
from wtforms.validators import DataRequired, Length, Required
from app.align_reader import AlignReader 


align_reader = AlignReader()

class VerseForm(Form):
    verse_id = StringField("verse_id")

class LoginForm(FlaskForm):
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
    source_language = SelectField('Source language: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    target_languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=align_reader.file_lang_name_mapping.items())
    query = StringField('source word:', validators=[Required()], render_kw={"placeholder":"Enter a word to translate"})
    
    submit = SubmitField('Translate')
