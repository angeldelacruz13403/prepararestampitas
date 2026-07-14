from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    subject = StringField("Asunto", validators=[DataRequired(), Length(min=3, max=180)])
    message = TextAreaField("Mensaje", validators=[DataRequired(), Length(min=10, max=5000)])
    submit = SubmitField("Enviar")
