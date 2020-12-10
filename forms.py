from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
                           InputRequired("Please enter a username")])
    password = PasswordField("Password", validators=[
                             InputRequired("Please enter a password")])
    email = StringField("Email", validators=[Email()])
    first_name = StringField("First Name", validators=[
                             InputRequired("Please enter your first name")])
    last_name = StringField("Last Name", validators=[
                            InputRequired("Please enter your last name")])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired("Please enter a username")])
    password = PasswordField("Password", validators=[
        InputRequired("Please enter a password")])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[
                        InputRequired("Please enter a title")])
    content = StringField("Content", validators=[
                          InputRequired("Please enter content")])
