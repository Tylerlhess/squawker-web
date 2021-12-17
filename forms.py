from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp
import re

VALID_RVN = re.compile('^(R|r)[a-zA-Z0-9]{33}')
VALID_RVN_TEST = re.compile('^(M|m)[a-zA-Z0-9]{33}')


class Register(FlaskForm):
    address = StringField('RVN address', validators=[Regexp(VALID_RVN)])


class tRegister(FlaskForm):
    address = StringField('tRVN address', validators=[Regexp(VALID_RVN_TEST)])


class SendKaw(FlaskForm):
    message = StringField('Kaw', validators=[DataRequired()])


class EditProfile(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    pictureHash = StringField('Picture Hash')
    pgp_pub_key = StringField('PGP_pub_key')
    bio = TextAreaField('Bio')







