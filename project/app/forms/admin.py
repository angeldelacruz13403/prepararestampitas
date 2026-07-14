from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=100)])
    slug = StringField("Slug", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Descripción")
    is_active = BooleanField("Activa", default=True)
    submit = SubmitField("Guardar")


class GalleryImageForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(min=2, max=150)])
    description = TextAreaField("Descripción")
    alt_text = StringField("ALT", validators=[Length(max=180)])
    category_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    image = FileField(
        "Imagen",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Formato no permitido"),
        ],
    )
    is_public = BooleanField("Pública", default=True)
    is_featured = BooleanField("Destacada", default=False)
    submit = SubmitField("Guardar")
