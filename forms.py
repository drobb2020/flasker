from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     TextAreaField, ValidationError)
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea


class NamerForm(FlaskForm):
    name = StringField("What's Your Name:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Full Name:", validators=[DataRequired()])
    username = StringField("Username:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    favorite_quote = TextAreaField("Favorite Quote:")
    about_author = TextAreaField("About Author:")
    password_hash = PasswordField("Password:", validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField("Confirm Password:", validators=[DataRequired()])
    profile_pic = FileField("Profile Picture:")
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's your Email:", validators=[DataRequired()])
    password_hash = PasswordField("What's your Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    title = StringField("Title:", validators=[DataRequired()])
    # content = TextAreaField("Content:", validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    # author = StringField("Author:")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
