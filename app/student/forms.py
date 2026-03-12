from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class ProfileForm(FlaskForm):
    course_class = StringField('Class (e.g. TE, SE)', validators=[DataRequired(), Length(max=50)])
    year = StringField('Academic Year (e.g. 2023-2024)', validators=[DataRequired(), Length(max=20)])
    branch = StringField('Branch', validators=[DataRequired(), Length(max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired()])
    nearest_station = StringField('Nearest Railway Station', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Update Profile')

class ConcessionApplicationForm(FlaskForm):
    journey_type = SelectField('Type of Journey', choices=[('First Class', 'First Class'), ('Second Class', 'Second Class')], validators=[DataRequired()])
    pass_duration = SelectField('Duration of Pass', choices=[('1 Month', '1 Month'), ('Quarterly', 'Quarterly')], validators=[DataRequired()])
    fee_receipt = FileField('Current Year Fee Receipt', validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'], 'PDFs and Images only!')])
    aadhaar_card = FileField('Aadhaar Card', validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'], 'PDFs and Images only!')])
    submit = SubmitField('Submit Application')
