from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=8, max=64)])
    remember_me = BooleanField("Recordarme")
    submit = SubmitField("Entrar")


class RegisterForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Registrarse")
