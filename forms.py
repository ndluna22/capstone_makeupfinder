from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class ReviewForm(FlaskForm):
    """Form for adding/editing reviews."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class ProfileEditForm(FlaskForm):
    """Form for editing profile."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('text', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


# class SearchForm(FlaskForm):
#     """Search form."""

#     name = StringField('Search by lipstick,blush,... ',
#                        id='words_autocomplete', validators=[DataRequired()])


class SelectFields(FlaskForm):
    """Search form."""

    name = SelectField('Choose an option', choices=[('Certclean', 'CertClean'), ('Chemical+Free', 'Chemical Free'), ('EWG+Verified', 'EWG Verified'), ('EcoCert', 'EcoCert'), ('Fair+Trade', 'Fair Trade'), ('Gluten+Free', 'Gluten Free'), ('Natural', 'Natural'), ('No+Talc', 'No Talc'), ('Non-GMO', 'Non-GMO'), ('Organic', 'Organic'), ('Peanut+Free+Product', 'Peanut Free Product'), ('Sugar+Free', 'Sugar Free'), ('USDA+Organic', 'USDA Organic'), ('Vegan', 'Vegan'), ('alcohol+free', 'alcohol free'), ('cruelty+free', 'cruelty free'), ('purpicks', 'purpicks'), ('silicone+free', 'silicone free'), ('water+free', 'water free')

                                                    ], validators=[DataRequired()])
    submit = SubmitField('Submit', validators=[DataRequired()])
