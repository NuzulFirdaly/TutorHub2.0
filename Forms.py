from wtforms import Form, FileField,StringField, RadioField, SelectField, TextAreaField, IntegerField, validators,SelectMultipleField, MultipleFileField, validators, PasswordField, BooleanField,FloatField , DateField
from wtforms.validators import EqualTo, DataRequired, Email, email_validator,Length,ValidationError
from wtforms.fields.html5 import DateField

class CreateUserForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])

    email = StringField('Email', [validators.Length(min=1,
                                                    max=150), validators.DataRequired(), validators.email()])
    username = StringField('Username', [validators.Length(min=8
                                                          ), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=8
                                                            ), validators.DataRequired(),
                                          EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=8
                                                          ), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=8
                                                            ), validators.DataRequired()])
    remember = BooleanField('Remember me')


class PersonalInfoForm(Form):
    first_name = StringField("First Name",[validators.Length(min=5, max=150), validators.DataRequired()])
    last_name = StringField([validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField([validators.Length(min=30,max=600), validators.InputRequired()])
    language = StringField('Language', [validators.Length(min=1, max=20), validators.DataRequired()], render_kw={'placeholder':"Language"})
    proficiency = SelectField('Proficiency', choices=[('Basic', 'Basic'), ('Conversational', 'Conversational'), ('Fluent', 'Fluent'), ('Native','Native/Bilingual')],render_kw={'placeholder':"proficiency"})

def nric_check(form,field):
    if not(field.data[0].isalpha() and field.data[-1].isalpha() and field.data[1:-2].isnumeric()):
        raise ValidationError('NRIC not valid')
class ProfessionalInfoForm(Form):
    occupation = StringField( validators =[DataRequired(), Length(min=5,max=60)])
    fromyear = StringField(validators =[DataRequired(), Length(min=4,max=4)])
    toyear = StringField(validators =[DataRequired(), Length(min=4,max=4)])
    college_country = StringField(validators =[DataRequired(), Length(min=4,max=30)])
    college_name = StringField(validators =[DataRequired(), Length(min=2,max=60)])
    major = StringField(validators =[DataRequired(), Length(min=5,max=60)])
    graduateyear = StringField(validators =[DataRequired(), Length(min=4,max=4)])
    dob = DateField(format='%Y-%m-%d')
    nric = StringField(validators =[DataRequired(), Length(min=9,max=9), nric_check])