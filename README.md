# estadiaSegura
Herramienta digital de gestión de servicios para alojamientos de Tierra del Fuego

Pasos para ejecutar correctamente Estadía Segura TDF:
Descargar e Instalar la versión de Python 3.9.2 desde https://www.python.org/downloads/ .
Ubicarse en el directorio ./proyecto.
Instalar los requerimientos del sistema:
pip install -r requirements.txt
Generar a base de datos:
py manage.py makemigrations
py manage.py migrate
Carga inicial:
py manage.py carga_inicial
Cargar los alojamientos:
py manage.py carga_alojamientos usuario contraseña
Se debe solicitar usuario y contraseña de acceso al SUIT (Sistema Unificado de Información Turística - https://suit.tur.ar/ ) al INFUETUR.
(Opcional) Carga de datos de ejemplo items-desayuno:
py manage.py loaddata
 ./estadiatdf/fixtures/items_desayuno.json
(Opcional) Iniciar servidor local smtpd en una nueva terminal para prueba de envío de correos:
py -m smtpd -n -c DebuggingServer localhost:1025
Ejecutar el servidor web local: 
py manage.py runserver
Se puede ingresar al sistema con el usuario creado por defecto:
Usuario: estadiatdf
Contraseña: Laboratorio2020
