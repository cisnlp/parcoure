from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, FieldList, FormField, Form, IntegerField, RadioField, FloatField
from wtforms.validators import DataRequired, Length, Required, Optional
from app.general_align_reader import GeneralAlignReader 
from app import stats
from app import utils


align_reader = GeneralAlignReader()


class VerseForm(Form):
    verse_id = StringField("verse_id")

class MultialignForm(FlaskForm):
    class Meta:
        csrf = False
    languages = SelectMultipleField('Target editions: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=list(align_reader.file_edition_mapping.items()))
    verse = StringField('Bible keywords:', default="", render_kw={"placeholder":"type to search verses...", "data-url":"search", "autocomplete":"off"})
    verses = FieldList(
        FormField(VerseForm),
        min_entries=0,
        max_entries=50
    )
    #recaptcha = RecaptchaField()
    submitField = SubmitField('Get Alignments')

class LexiconForm(FlaskForm):
    class Meta:
        csrf = False
    source_language = SelectField('Source language: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=[(x,x) for x in align_reader.all_langs])
    target_languages = SelectMultipleField('Target languages: ', validators=[Required()], render_kw={'data-live-search': 'true'}, choices=[(x,x) for x in align_reader.all_langs])
    query = StringField('source word:', validators=[Required()], render_kw={"placeholder":"enter a word to translate"})
    #recaptcha = RecaptchaField()
    submitField = SubmitField('Get Translations')

class statsForm(FlaskForm):
    valid_edition_1 = list(align_reader.file_edition_mapping.items())[:]
    
    for edition in valid_edition_1[:]:
        if (not edition[0].startswith('eng') or edition[0].startswith('prs')) and utils.is_pbc:
            valid_edition_1.remove(edition)

    stat_type = SelectField('stat type', validators=[Required()], choices=stats.stat_types)
    if utils.is_pbc:
        lang1 = SelectField('Language 1', validators=[Optional()], choices = [('eng', 'eng'), ('prs', 'prs')])
    else:
        lang1 = SelectField('Language 1', validators=[Optional()], choices = [(x,x) for x in align_reader.all_langs])
    lang2 = SelectField('Language 2', validators=[Optional()], choices = [(x,x) for x in align_reader.all_langs])
    edition_1 = SelectField('Edition 1', validators=[Optional()], choices = valid_edition_1)
    edition_2 = SelectField('Edition 2', validators=[Optional()], choices = list(align_reader.file_edition_mapping.items()))
    
    minimum = FloatField('Min', validators=[Optional()])
    maximum = FloatField('Max', validators=[Optional()])
    bin_count = IntegerField('Bin count', validators=[Optional()], render_kw={"placeholder":20})

    # if len(utils.config_parser['section']['CAPTCHA_SITE_KEY'] > 0 and utils.config_parser['section']['CAPTCHA_SECRET_KEY'] > 0):
    #     recaptcha = RecaptchaField()
    submitField = SubmitField('Get Stats')


class AlignForm(FlaskForm):
    english = StringField('Sentence A:', validators=[DataRequired(), Length(
        min=1, max=500, message="INPUT TOO LONG")], default="")
    foreign = StringField('Sentence B:', validators=[DataRequired(), Length(min=1, max=500, message="INPUT TOO LONG")])
    model = RadioField('Model', choices=[('bert', 'mBERT'), ('xlmr', 'XLM-R')], default="bert")
    # method = RadioField('Method', choices=[('inter', 'ArgMax'), ('itermax',
    #                                                              'IterMax'), ('mwmf', 'Match')], default="itermax")
    # if len(utils.config_parser['section']['CAPTCHA_SITE_KEY'] > 0 and utils.config_parser['section']['CAPTCHA_SECRET_KEY'] > 0):
    #     recaptcha = RecaptchaField()
    submitField = SubmitField('Align')

class MultialignInputForm(FlaskForm):
    class Meta:
        csrf = False
    sentences = FieldList(
        FormField(VerseForm),
        min_entries=2,
        max_entries=50
    )
    submitField = SubmitField('Get Alignments')