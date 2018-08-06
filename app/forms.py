from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired
from app.helpers import dists, sen_dists

class DistrictForm(FlaskForm):
    select_district = SelectField(u'District', choices=dists)
    district_time_delta = SelectField(u'Time period', choices=[
            ('1', 'Last 24 hours'),
            ('2', 'Last 48 hours'),
            ('7', 'Last week'),
            ('28', 'Last 4 weeks'),
    ])
    submit_district = SubmitField('Submit your choice')

class SenForm(FlaskForm):
    select_district = SelectField(u'State', choices=sen_dists)
    district_time_delta = SelectField(u'Time period', choices=[
            ('1', 'Last 24 hours'),
            ('2', 'Last 48 hours'),
            ('7', 'Last week'),
            ('28', 'Last 4 weeks'),
    ])
    submit_district = SubmitField('Submit your choice')

class HashtagSearchForm(FlaskForm):
    hashtag_search = StringField('Hashtag', validators=[DataRequired()])
    #phrase_search = StringField('phrase search', validators=[DataRequired()])
    hashtag_time_delta = SelectField(u'Time period', choices=[
            ('1', 'Last 24 hours'),
            ('2', 'Last 48 hours'),
            ('7', 'Last week'),
            ('28', 'Last 4 weeks'),
    ])
    submit_hash = SubmitField('Submit your choice')

class PhraseSearchForm(FlaskForm):
    phrase_search = StringField('phrase search', validators=[DataRequired()])
    ####time_period TODO
    submit_phrase = SubmitField('Submit your choice')

class AllCongSearchForm(FlaskForm):
    scope_search = SelectField(u'Scope', choices=[
            ('allcong', 'All competitive 2018 House races'),
            ('allsen', 'All competitive 2018 Senate races'),
            ('allraces', 'All competitive 2018 congressional races'),
    ])
    #phrase_search = StringField('phrase search', validators=[DataRequired()])
    allcong_time_delta = SelectField(u'Time period', choices=[
            ('1', 'Last 24 hours'),
            ('2', 'Last 48 hours'),
            ('7', 'Last week'),
            ('28', 'Last 4 weeks'),
    ])
    submit_allcong_search = SubmitField('Submit your choice')

class BotSearchForm(FlaskForm):
    scope_search = SelectField(u'Scope', choices=[
            ('allbots', 'Activity by all bot-like users')
    ])
    #phrase_search = StringField('phrase search', validators=[DataRequired()])
    botform_time_delta = SelectField(u'Time period', choices=[
            ('1', 'Last 24 hours'),
            ('2', 'Last 48 hours'),
            ('7', 'Last week'),
            ('28', 'Last 4 weeks'),
    ])
    submit_botform_search = SubmitField('Submit your choice')

class ChangeTimeForm(FlaskForm):
    scope_field = HiddenField(u'', validators=[DataRequired()])
    url_field = HiddenField(u'', validators=[DataRequired()])
    change_time_delta = SelectField(u'Time period', choices=[
            ('1', 'Last 24 hours'),
            ('2', 'Last 48 hours'),
            ('7', 'Last week'),
            ('28', 'Last 4 weeks'),
    ])
    submit_change_time = SubmitField('Submit')
