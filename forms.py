from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
import pycountry

class PostForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(min=1, max=300)])
    description = TextAreaField('Description', validators=[InputRequired(), Length(min=100, max=4000) ])

class SubmissionForm(Form):
    comment = TextAreaField('Comment', validators=[InputRequired(), Length(min=1, max=4000)])

class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_2, country.name) for country in pycountry.countries]

class RegistrationForm(Form):
    name = StringField('Name', validators=[InputRequired(), Length(max=60)])
    username = StringField('Username', validators=[InputRequired(), Length(max=15)])
    email = StringField("Email",  [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match'),
        Length(min=6, max=30)
    ])
    confirm = PasswordField('Repeat Password')
    occupation = StringField('Occupation', validators=[InputRequired(), Length(max=100)])
    country = CountrySelectField('Country', validators=[InputRequired()])

class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired(), Length(max=15)])
    password = PasswordField('Password', [
        DataRequired(),
        Length(min=6, max=30)
    ])