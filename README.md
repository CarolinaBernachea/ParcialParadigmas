# supreme-happiness

## Instalar

Con `pipenv` instalado en tu máquina, ejecutá dentro del directorio del
repositorio:

```bash
pipenv install
```
 
#----------------------------------------------------------- INFORME DE PROGRAMA -----------------------------------------------------------#

##Preuso##
Actualizar a la version 2.2.1 del modulo WTform dentro del enviroment.

##Flujo del programa y funciones que se crearon##
#carga_csv#
	> Se crean 2 listas vacias que van a servir para guardar la información de los CSV subidos.
	> Si el usuario está en sesion y apreta el boton con un "if", "else" chequea si se selecciónó algun archivo.
	> Si no se seleccionó ninguno, se muestra un "Flash".
	> Si se seleccionó, chequea extensión y verificaciones.
	> Si hay errores en la verificación del CSV, muestra errores.
	> Si está OK, se copia en el Consolidado.
	> Finalmente se pasan las listas de los archivos mal, y los archivos bien, como cookies, para mostrarlas luego en otra pagina. (\post_carga)

#post_carga#
	> Pagina de redireccionamiento luego de cargar el CSV
	> Si estuvo todo OK, te muestra el nombre de los achivos cargados correctamente.
	> Si hubieron archivos subidos con problemas, te enlista los problemas.

#buscador#
	> Se crean listas temporales para guardar la información solicitada mas adelante.
	> Con un "if" se chequea que, una vez apretado el boton, se abra y lea el archivo.
	> Si lo que el usuario ingresó, tiene 3 caracteres o mas, que agregue a las listas los matcheos de "PRODUCTOS" y "CLIENTES"
	> "else", tiene menos de 3 caracteres, muestra "Flash" indicando error. 
	> Se pasan las listas temporales, como cookies, para mostrarlas luego en otra página. (\buscador_resultado)

#buscador_resultado#
	> Pagina de redireccionamiento donde se muestran los resultados hechos en \buscador.

#cliente#
	> Se crean dos listas vacias que se usaran mas adelante para el guardado de la información.
	> Con un "with open", se abre el archivo consolidado y se lee con el csv.reader.
	> Itero con un "for" en las lineas y le paso instrucción "if" linea es igual a 0 (Encabezado), me lo agrege a la lista de encabezado que cree.
	> Instruccion "if", cliente que se buscó está en la linea, índex [2] (Sería columna 3 del CSV - CLIENTE), me lo agrega a la lista de clientes que cree. 
	> Le paso las listas como cookies

#producto#
	> Se crean las listas vacias para ser usadas mas adelante.
	> Abro el archivo, y repito los pasos de #cliente#, pero centrandome esta vez en el índex [1] (Columna 2 del CSV - PRODUCTO)
	> "if" producto está en linea index [1], me lo agrega a la lista de productos.
	> Le paso las listas como cookies.

#mas_vendidos#
	> "if" usuario toca el botón, se abre y lee el consolidado.
	> Itero linea por linea con un "for".
	> if linea está en 0 (Encabezado) apendea los index [0][1][3] (CODIGO - PRODUCTO - CANTIDAD)
	> "try" buscar el nombre del producto en la lista, dentro de la lista
	> "if" lo encuentra, le suma la cantidad, "else", lo agrega a la lista
	> Con un "sorted" se ordenan los datos, y el "reverse=True" para que los muestre de MAYOR a MENOR
	> Le paso las listas como cookies

#mas_vendidos_resultado#
	> Página de redireccionamiento donde me renderiza el template de los resultados mas vendidos.

#mas_gastados#
	> "if" usuario toca el botón, se abre y lee el consolidado.
	> Itero linea por linea con un "for".
	> if linea está en 0 (Encabezado) apendea los index [2][4] (CLIENTE - PRECIO)
	> "try" buscar el nombre del cliente en la lista, dentro de la lista
	> "if" lo encuentra, le suma lo gastado (Precio), "else", lo agrega como nuevo
	> Con un "sorted" se ordenan los datos, y el "reverse=True" para que los muestre de MAYOR a MENOR
	> Le paso las listas como cookies

#mas_gastados_resultado#
	> Página de redireccionamiento donde me renderiza el template de los clientes que mas plata gastaron.

#archivos_permitidos#
	> Se parte el nombre del archivo en 2 poniendo ambos elementos en una lista y si el segundo elemento (la extension) se encuentra adentro de el set de archivos permitidos entonces devuelve true sino false

#Extra:#
	> De las funciones ya explicadas, se crearon 4 clases en el archivo forms.py, para poder tomar el input del usuario

##•ACLARACION PARA TODAS LAS FUNCIONES•##
	> Todas las funciones se redireccionarán correctamente si y solo sí el usuario esta en session (logeado)
	> Caso contrario, será redirigido a una página, donde se le indicará que no tiene permiso apra estar allí.

##¿Qué estructura se utilizará para representar la información del archivo?##
	> Se utilizaron 2 métodos:
		> Uno de ellos fue crear una lista para el encabezado y otra lista, que contenia listas, para los datos. 
		> Otro metodo fue, guardar en un diccionario el encabezado para referenciar las columnas, que podían ser aleatorias.
	> Se creó una clase "CargarCSVForm", en la cuál se pasa un 'file' como "MultipleFileFields()" --> Que es un objeto para poder seleccionar varios archivos a la vez. Y el "SubmitField" --> Que es el boton que carga el archivo. 

##Como se usa el programa:##
#1
	> El usuario debe logearse a la página con usuario y contraseña para poder ingresar.
#2
	> En caso de no estar registrado, se dirige al boton "Registrarse", y procede a registrarse. 
#3
	> Las credenciales quedan guardadas en un archivo CSV.
#4
	> Una vez logueado, y dentro del sistema, puede cargar su propio archivo/s CSV.
#5
	> Si el archivo presenta fallas, serán indicadas en la post carga los errores encontrados, caso contrario se listan los archivos subidos correctamente.
#6
	> En la seccion "Buscador", el usuario podra filtrar la busqueda en la base de datos, ya sea por "PRODUCTO" o por "CLIENTE". Ingresando un mínimo de 3 carácteres, la página le mostrará todos los matcheos encontrados, tanto de "CLIENTES" como de "PRODUCTOS".
#7
	> Seleccionada la opción deseada, el programa le mostrará la tabla "PRODUCTOS" o "CLIENTES" según lo que el usuario haya seleccionado.
#8
	> En la seccion "Mas vendidos", encontraremos un buscador, en el cuál se deberá ingresar un número entero, el cuál será el rango de "PRODUCTOS MAS VENDIDOS", que se quisiera mostrar. Si se ingresa como parámetro un "2", se listarán los 2 "PRODUCTOS" más vendidos, mostrando su cantidad de mayor a menor. 
#9
	> En la sección "Mejores Clientes", encontraremos un buscador en el cuál se deberá ingresar un número entero, igual que en el caso anterior, que será el rango de "CLIENTES QUE MAS GASTARON" que se quieran mostrar. Entonces, si el usuario ingresa un 5, se listarán los 5 clientes que mas gastaron, ordenados de mayor a menor. 
#10
	> Para salir de la sesión, se deberá dirigir al boton "Cerrar Sesión", y se dará por finalizada la misma. 

#Aclaración#
•Existe persistencia de datos en la base para futuras consultas.•

