#!/usr/bin/env python
import os
import csv
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap
# from flask_moment import Moment
from flask_script import Manager
from forms import LoginForm, SaludarForm, RegistrarForm, CargarCSVForm, BuscarForm, VendidosForm, GastadosForm
from werkzeug.utils import secure_filename

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
# moment = Moment(app)

app.config['SECRET_KEY'] = 'un string que funcione como llave'


@app.route('/')
def index():
	if 'username' in session:
		list_clientes = []
		list_header = []
		archivo = []
		#lee el archivo de abajo para arriba
		with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'r') as abrir_con:
			reader_tmp = csv.reader(abrir_con)
			for linea in reader_tmp:
				archivo.append(linea)	
		for index_linea, linea in enumerate(reversed(archivo)):
			if index_linea == len(archivo)-1:
				list_header.append(linea)
			else: 
				list_clientes.append(linea)
		session['list_clientes'] = list_clientes
		session['list_header'] = list_header
	return render_template('index.html', fecha_actual=datetime.utcnow())


@app.route('/saludar', methods=['GET', 'POST'])
def saludar():
    formulario = SaludarForm()
    if formulario.validate_on_submit():
        return redirect(url_for('saludar_persona', usuario=formulario.usuario.data))
    return render_template('saludar.html', form=formulario)


@app.route('/saludar/<usuario>')
def saludar_persona(usuario):
    return render_template('usuarios.html', nombre=usuario)


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        with open('usuarios') as archivo:
            archivo_csv = csv.reader(archivo)
            registro = next(archivo_csv)
            while registro:
                if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                    flash('Ingresó correctamente')
                    session['username'] = formulario.usuario.data
                    return render_template('index.html')
                registro = next(archivo_csv, None)
            else:
                flash('Revisá nombre de usuario y contraseña')
                return redirect(url_for('ingresar'))
    return render_template('login.html', formulario=formulario)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = RegistrarForm()
    if formulario.validate_on_submit():
        if formulario.password.data == formulario.password_check.data:
            with open('usuarios', 'a+') as archivo:
                archivo_csv = csv.writer(archivo)
                registro = [formulario.usuario.data, formulario.password.data]
                archivo_csv.writerow(registro)
            flash('Usuario creado correctamente')
            return redirect(url_for('ingresar'))
        else:
            flash('Las contraseñas no coinciden')
    return render_template('registrar.html', form=formulario)


@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html')
    else:
        return render_template('sin_permiso.html')


@app.route('/carga_csv', methods=['GET', 'POST'])
def carga_csv():
	archivos_problemas = []
	archivos_bien = []
	#chequea si esta logueado
	if 'username' in session:
		#crea el formulario CSV
		formulario = CargarCSVForm()
		#Si el boton es apretado
		if formulario.validate_on_submit():
			#chequea si se cargo algun archivo
			if(request.files['file'] == ""):
				flash('Por favor seleccionar un archivo')
			else: 
				#itera todos los archivos seleccionados
				for arch_subido in request.files.getlist('file'):
					#revisa que no haya problemas con el nombre
					nom_arch_subido = secure_filename(arch_subido.filename)
					#Guarda el archivo temporalmente en la carpeta tmp
					arch_subido.save(os.path.join("tmp/", nom_arch_subido))
					#chequea si la extension es correcta
					if archivos_permitidos(arch_subido.filename):
						#Abre el archivo
						mal_gen = False
						tmp_col_encabezado = {}
						with open(os.path.join("tmp/", nom_arch_subido), 'r') as abrir_tmp:
							mal_col = False
							chequear_formato = re.compile("^[A-Z]{3}[0-9]{3}$")
							reader_tmp = csv.reader(abrir_tmp)
							#HACE LAS COMPROBACIONES CORRESPONDIENTES
							for num_linea, lineas in enumerate(reader_tmp):
								mal_vacia = False
								#Guarda las posiciones del encabezado en un diccionario
								if (num_linea == 0):
									for xEncabezado in ["CODIGO","PRODUCTO","CLIENTE","CANTIDAD","PRECIO"]:
										try:
											tmp_col_encabezado[xEncabezado] = lineas.index(xEncabezado)

										#Si falta una columna o un encabezado no tiene el nombre apropiado tira error y no te chequea lo demas
										except ValueError:
											if (len(lineas) != 5):
												archivos_problemas.append("La cantidad de columnas " + str(len(lineas)) + " es incorrecta. Archivo: " + nom_arch_subido)
												mal_col = True
												mal_gen = True
											else:
												archivos_problemas.append("Nombre de columna erroneo. Archivo: " + nom_arch_subido)
												mal_col = True
												mal_gen = True
											break
								if(mal_col == True):
									break
								#Comprueba que no tiene celdas vacias
								for xElem in lineas:
									if (xElem == "" and mal_vacia == False):
										archivos_problemas.append("Celda vacia en la linea " + str(num_linea + 1) + ". Archivo: " + nom_arch_subido)
										mal_vacia = True
										mal_gen = True
								#Comprueba que la columna codigo tiene un formato correcto
								if(num_linea != 0): #si no es el encabezado
									if not chequear_formato.match(lineas[tmp_col_encabezado["CODIGO"]]):
										archivos_problemas.append("Codigo incorrecto en la linea " + str(num_linea + 1) + ". Archivo: " + nom_arch_subido)
										mal_gen = True
								#Compruebo que la columna cantidad sean enteros y 
								if(num_linea != 0): #si no es el encabezado
									try:
										int(lineas[tmp_col_encabezado["CANTIDAD"]])
									except ValueError:
										archivos_problemas.append("Numero incorrecto en la columna CANTIDAD, linea " + str(num_linea + 1) + ". Archivo: " + nom_arch_subido)
										mal_gen = True
									#Compruebo la columna precio sea decimal
									try:
										int(lineas[tmp_col_encabezado["PRECIO"]])
										archivos_problemas.append("Numero incorrecto en la columna PRECIO, linea " + str(num_linea + 1) + ". Archivo: " + nom_arch_subido)
										mal_gen = True
									except ValueError:
										try:
											float(lineas[tmp_col_encabezado["PRECIO"]])
										except ValueError:
											archivos_problemas.append("Numero incorrecto en la columna PRECIO, linea " + str(num_linea + 1) + ". Archivo: " + nom_arch_subido)
											mal_gen = True
					else: 
						archivos_problemas.append("Archivo: " + nom_arch_subido + " tiene una extension incorrecta")
						mal_gen = True
					#Si el archivo esta OK se copia y pega en el consolidado compania
					if (mal_gen == False):
						archivos_bien.append(nom_arch_subido)
						with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'a', newline='') as abrir_consolidado:
							cons_writer = csv.writer(abrir_consolidado)
							with open(os.path.join("tmp/", nom_arch_subido), 'r') as abrir_tmp:
								reader_tmp = csv.reader(abrir_tmp)
								#Saltea encabezado
								next(reader_tmp, None)
								#Recorro las lineas del temporal
								for tmp_lineas in reader_tmp:
										cons_writer.writerow([tmp_lineas[tmp_col_encabezado["CODIGO"]]] + [tmp_lineas[tmp_col_encabezado["PRODUCTO"]]] + [tmp_lineas[tmp_col_encabezado["CLIENTE"]]] + [tmp_lineas[tmp_col_encabezado["CANTIDAD"]]] + [tmp_lineas[tmp_col_encabezado["PRECIO"]]])
					os.remove(os.path.join("tmp/", nom_arch_subido))
			#Le paso las listas como cookies para que se puedan levantar del html en otra pagina
			session['form_arch_bien'] = archivos_bien
			session['form_arch_mal'] = archivos_problemas

			return redirect(url_for('post_carga'))

		return render_template('carga_csv.html', formulario=formulario)
	else:
		return render_template('sin_permiso.html')


@app.route('/logout', methods=['GET'])
def logout():
	if 'username' in session:
		session.pop('username')
		return render_template('logged_out.html')
	else:
		return redirect(url_for('index'))


@app.route('/post_carga', methods=['GET'])
def post_carga():
	#Diplay de errores
	if 'username' in session:
		return render_template('post_carga.html')
	else:
		return redirect(url_for('sin_permiso.html'))

@app.route('/buscador', methods=['GET', 'POST'])
def buscador():
	formulario = BuscarForm()
	if 'username' in session:
		menor_a_tres = True
		list_tmp_clientes = []
		list_tmp_productos = []
		#Cuando se apreta el boton
		if formulario.validate_on_submit():
			with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'r') as abrir_con:
				#Chequea que lo ingresado tenga minimo 3 caracteres
				if(len(formulario.buscar.data) >= 3):
					menor_a_tres = False
					reader_con = csv.reader(abrir_con)
					#lee el archivo linea por linea
					for index_lineas, lineas in enumerate(reader_con):
						#Si no es el encabezado
						if (index_lineas != 0):
							#lee el dato en la columna productos y clientes y se fija si lo que inserto el usuario esta y lo agrega a la lista que corresponde
							if(formulario.buscar.data.lower() in lineas[1].lower()):
								list_tmp_productos.append(lineas[1])
							if(formulario.buscar.data.lower() in lineas[2].lower()):
								list_tmp_clientes.append(lineas[2])
				#Si tiene menos de 3 caracteres
				else:
					flash("Inserte minimo 3 caracteres")
			if menor_a_tres == False:
				#Le paso las listas como cookies para que se puedan levantar del html en otra pagina
				session['buscado_clientes'] = list(set(list_tmp_clientes))
				session['buscado_productos'] = list(set(list_tmp_productos))
				return redirect(url_for('buscador_resultado'))
		return render_template('buscador.html',formulario=formulario)
	else:
		return redirect(url_for('sin_permiso.html'))


@app.route('/buscador_resultado', methods=['GET'])
def buscador_resultado():
	if 'username' in session:
		return render_template('buscador_resultado.html')
	else:
		return redirect(url_for('sin_permiso.html'))

@app.route('/cliente/<cliente>')
def cliente(cliente):
	if 'username' in session:
		lista_productos = []
		lista_header = []
		#Abre el archivo consolidado compania
		with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'r') as abrir_con:
			reader_con = csv.reader(abrir_con)
			#Lo lee linea por linea
			for num_linea, linea in enumerate(reader_con):
				if num_linea == 0:
					lista_header.append(linea)
				#Si esta el cliente seleccionado en la columna 3 lo agrega a la lista
				if cliente in linea[2]:
					lista_productos.append(linea)
		#Le paso las listas como cookies para que se puedan levantar del html en otra pagina
		session["listado_productos"] = lista_productos
		session["listado_header"] = lista_header
		return render_template('cliente.html', usuario = cliente)
	else:
		return redirect(url_for('sin_permiso.html'))

@app.route('/producto/<producto>')
def producto(producto):
	if 'username' in session:
		lista_productos = []
		lista_header = []
		#Abre el archivo consolidado compania
		with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'r') as abrir_con:
			reader_con = csv.reader(abrir_con)
			#Lo lee linea por linea
			for num_linea, linea in enumerate(reader_con):
				if num_linea == 0:
					lista_header.append(linea)
					#Si esta el cliente seleccionado en la columna 2 lo agrega a la lista
				if(producto in linea[1]):
					lista_productos.append(linea)
		#Le paso las listas como cookies para que se puedan levantar del html en otra pagina
		session["listado_productos"] = lista_productos
		session["listado_header"] = lista_header
		return render_template('producto.html', prod = producto)
	else:
		return redirect(url_for('sin_permiso.html'))



@app.route('/mas_vendidos', methods=['GET', 'POST'])
def mas_vendidos():
	formulario = VendidosForm()
	if 'username' in session:
		error_input = False
		list_productos = []
		list_header = []
		real_list = []
		#Si toca el boton
		if formulario.validate_on_submit():
			#Chequeo que sea un numero entero
			try:
				int(formulario.buscar.data)
			except ValueError:
				error_input = True

			if error_input == False:
				#Abre el archivo consolidado compania
				with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'r') as abrir_con:
					reader_con = csv.reader(abrir_con)
					#Lo lee linea por linea
					for index_linea, linea in enumerate(reader_con):
						encontrado = False
						#Appendea el encabezado a la lista encabezado
						if index_linea == 0:
							list_header.append([linea[0], linea[1], linea[3]])
						else:
							#Recorre la lista de productos
							for index_elemento, elemento in enumerate(list_productos):
								try:
									#Busca si esta el nombre del producto en la lista dentro de la lista
									elemento.index(linea[1])
									encontrado = True
									index_elemento_encontrado = index_elemento
								except:
									continue
							#Si no lo encontro lo agrega como nuevo
							if encontrado == False:
								list_productos.append([linea[0], linea[1], linea[3]])
							#Si el producto esta agregado, le suma la cantidad
							else:
								list_productos[index_elemento_encontrado][2] = int(list_productos[index_elemento_encontrado][2]) + int(linea[3])
				#Ordena la lista de mayor a menor y la guarda en una nueva lista ordenada
				sorted_list = sorted(list_productos, key=lambda x: int(x[2]), reverse=True)
				#Le paso las listas como cookies para que se puedan levantar del html en otra pagina
				session['mas_vendidos_datos'] = (sorted_list[:int(formulario.buscar.data)])
				session['mas_vendidos_header'] = list_header
				return redirect(url_for('mas_vendidos_resultado'))
			else:
				flash("Por favor inserte un numero válido")
				
		return render_template('mas_vendidos.html', formulario=formulario)
	else:
		return redirect(url_for('sin_permiso.html'))


@app.route('/mas_vendidos_resultado', methods=['GET'])
def mas_vendidos_resultado():
	if 'username' in session:
		return render_template('mas_vendidos_resultado.html')
	else:
		return redirect(url_for('sin_permiso.html'))

@app.route('/mas_gastados', methods=['GET', 'POST'])
def mas_gastados():
	formulario = GastadosForm()
	if 'username' in session:
		error_input = False
		list_clientes = []
		list_header = []
		real_list = []
		#Si toca el boton
		if formulario.validate_on_submit():
			#Chequeo que sea un numero entero
			try:
				int(formulario.buscar.data)
			except ValueError:
				error_input = True

			if error_input == False:
				#Abre el archivo consolidado compania
				with open(os.path.join("ventas_db/Consolidado_Compania.csv"), 'r') as abrir_con:
					reader_con = csv.reader(abrir_con)
					#Lo lee linea por linea
					for index_linea, linea in enumerate(reader_con):
						encontrado = False
						#Appendea el encabezado a la lista encabezado
						if index_linea == 0:
							list_header.append([linea[2], linea[4]])
						else:
							#Recorre la lista de clientes
							for index_elemento, elemento in enumerate(list_clientes):
								try:
									#Busca si esta el nombre del cliente en la lista dentro de la lista
									elemento.index(linea[2])
									encontrado = True
									index_elemento_encontrado = index_elemento
								except:
									continue
							#Si no lo encontro lo agrega como nuevo
							if encontrado == False:
								list_clientes.append([linea[2], float(linea[4]) * int(linea[3])])
							#Si el cliente esta agregado, le suma lo gastado
							else:
								list_clientes[index_elemento_encontrado][1] = round(float(list_clientes[index_elemento_encontrado][1]) + (float(linea[4]) * int(linea[3])) ,2)
				sorted_list = sorted(list_clientes, key=lambda x: float(x[1]), reverse=True)
				#Le paso las listas como cookies para que se puedan levantar del html en otra pagina
				session['mas_gastados_datos'] = (sorted_list[:int(formulario.buscar.data)])
				session['mas_gastados_header'] = list_header
				return redirect(url_for('mas_gastados_resultado'))
			else:
				flash("Por favor inserte un numero válido")
		return render_template('mas_gastados.html', formulario=formulario)
	else:
		return redirect(url_for('sin_permiso.html'))


@app.route('/mas_gastados_resultado', methods=['GET'])
def mas_gastados_resultado():
	if 'username' in session:
		return render_template('mas_gastados_resultado.html')
	else:
		return redirect(url_for('sin_permiso.html'))


#Chequea extension del archivo
def archivos_permitidos(filename):
	extensiones_permitidas = set(['csv'])
	if (filename.rsplit('.', 1)[1].lower() in extensiones_permitidas):
		return True
	else:
		return False


if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)
    manager.run()
