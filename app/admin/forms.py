from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Optional, NumberRange
from app.models import User, Produk

class UserRoleForm(FlaskForm):
    role = SelectField('Role', choices=[('pending', 'Pending'), ('staf', 'Staf'), ('admin', 'Admin'), ('superadmin', 'Superadmin')], validators=[DataRequired()])
    submit = SubmitField('Update Role')

class ProductForm(FlaskForm):
    name = StringField('Nama Produk', validators=[DataRequired()])
    price = StringField('Harga', validators=[DataRequired()]) # Use StringField for price for now, convert to int/float later
    stock = StringField('Stok', validators=[DataRequired()])   # Use StringField for stock for now
    category = StringField('Kategori', validators=[Optional()])
    image = StringField('URL Gambar (Opsional)', validators=[Optional()])
    submit = SubmitField('Simpan Produk')

class IncomingProductForm(FlaskForm):
    product_id = SelectField('Pilih Produk', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Jumlah Barang Masuk', validators=[DataRequired(), NumberRange(min=1, message='Jumlah harus lebih dari 0.')])
    submit = SubmitField('Input Barang Masuk')

class OutgoingProductForm(FlaskForm):
    product_id = SelectField('Pilih Produk', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Jumlah Barang Keluar', validators=[DataRequired(), NumberRange(min=1, message='Jumlah harus lebih dari 0.')])
    submit = SubmitField('Input Barang Keluar')
