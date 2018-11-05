from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, MultipleFileField
from wtforms.validators import Required


class LoginForm(FlaskForm):
    usuario = StringField('Nombre de usuario', validators=[Required()])
    password = PasswordField('Contraseña', validators=[Required()])
    enviar = SubmitField('Ingresar')

class BuscarForm(FlaskForm):
	buscar = StringField('Buscar cliente o producto', validators=[Required()])
	enviar = SubmitField('OK!')

class VendidosForm(FlaskForm):
    buscar = StringField('Inserte un numero de registros a listar', validators=[Required()])
    enviar = SubmitField('OK!')

class GastadosForm(FlaskForm):
    buscar = StringField('Inserte un numero de registros a listar', validators=[Required()])
    enviar = SubmitField('OK!')

class SaludarForm(FlaskForm):
    usuario = StringField('Nombre: ', validators=[Required()])
    enviar = SubmitField('Saludar')

class RegistrarForm(LoginForm):
    password_check = PasswordField('Verificar Contraseña', validators=[Required()])
    enviar = SubmitField('Registrarse')

class CargarCSVForm(FlaskForm):
	file = MultipleFileField()
	enviar = SubmitField('Cargar Archivos')
