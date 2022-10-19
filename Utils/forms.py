from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FieldList, SubmitField
from wtforms.validators import DataRequired, Regexp
import re

VALID_RVN = re.compile('^(R|r)[a-zA-Z0-9]{33}')
VALID_RVN_TEST = re.compile('^(M|m)[a-zA-Z0-9]{33}')


class Login(FlaskForm):
    signstring = StringField('Message to sign')
    address = StringField('RVN address', validators=[Regexp(VALID_RVN)])
    nft = StringField('NFT')
    signature = StringField('Signature')
    signin = SubmitField("Sign in")


class EditProfile(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    profile_picture = StringField('Picture Hash')
    aet = StringField('AET NFT')
    bio = TextAreaField('Bio')
    jsonString = StringField('jsonString')
    extraFields = TextAreaField(['Bonus'])
    address = StringField('address')
    signature_hash = StringField('Signature Hash')
    signature = StringField('Signature')


class MarketAsset(FlaskForm):
    asset = StringField('Asset Channel', validators=[DataRequired()])


class AETRedemption(FlaskForm):
    ravencoinAddress = StringField('Ravencoin Address')
    pgpPubkey = TextAreaField('PGP_pub_key')
    signatureHash = StringField('Signature Hash')
    signature = StringField('Signature')


class SendKaw(FlaskForm):
    address = StringField('Ravencoin Address')
    kaw = TextAreaField('Kaw')
    signature_hash = StringField('Signature Hash')
    signature = StringField('Signature')
    media = FieldList(StringField('Media'))
    jsonString = StringField('jsonString')


class ReplyKaw(FlaskForm):
    address = StringField('Ravencoin Address')
    kaw = TextAreaField('Kaw')
    signature_hash = StringField('Signature Hash')
    signature = StringField('Signature')
    reply_to_txid = StringField('Reply To TXID')
    reply_to_url = StringField('Reply To URL')
    media = FieldList(StringField('Media'))
    jsonString = StringField('jsonString')

class PublishArticle(FlaskForm):
    address = StringField('Ravencoin Address')
    support_address = StringField('New Ravencoin Address')
    article_title = StringField('Title')
    article_version = StringField('Version')
    article = TextAreaField('Article')
    signature_hash = StringField('Signature Hash')
    signature = StringField('Signature')
    media = FieldList(StringField('Media'))
    jsonString = StringField('jsonString')

class CNSRecord(FlaskForm):
    address = StringField('RVN Asset Address')
    domain = StringField('Ravencoin Asset')
    aRecord = StringField('A record')
    aaaaRecord = StringField('AAAA record')
    cName = StringField('CName')
    mxRecord = StringField('MX record')
    txtRecords = TextAreaField("txt records")
    signature_hash = StringField('Signature Hash')
    signature = StringField('Signature')


ALL_FORMS = {
    "login": Login,
    "editProfile": EditProfile,
    "marketAsset": MarketAsset,
    "aetRedemption": AETRedemption,
    "sendKaw": SendKaw,
    "replyKaw": ReplyKaw,
    "publishArticle": PublishArticle,
}