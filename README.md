# GetHorarioDeClases
(Para estudiantes de la UC3M) Aplicacion que te descarga el horario de clases directamente desde aula global y lo importa a un nuevo calendario de Google

Download your classes schedule from Aula Global and import it to a new Google Calendar using your account.

**Section Shortcuts**:

- [Instrucciones en Español](https://github.com/Josersanvil/GetHorarioDeClases/blob/master/README.md#instrucciones-español)

- [English Instructions](https://github.com/Josersanvil/GetHorarioDeClases/blob/master/README.md#instructions-english)

## Instrucciones (Español)

### Instalación

Requiere python>=3.5

1. Descarga el repositorio en tu PC/Mac desde https://github.com/simonsanvil/GetHorarioDeClases 

2. Luego usa:
```
$ pip install -r requirements.txt
```
Para instalar todas las dependencias del proyecto.

### Instrucciones

1. Ejecuta el script HorarioDeClases_app.py en tu consola `python HorarioDeClases_app.py`
2. Sigue las instrucciones de la consola, introduce tu numero NIA y contraseña de AulaGlobal (esta informacion se mantiene dentro de tu equipo)
3. Inicia sesion con Google cuando se requiera y acepta los permisos de la aplicacion. Esto solo en necesario hacer la primera vez que corres el programa 
4. Espera a que el programa acabe de ejecutarse y listo! (puede que demore un poco)

### Preguntas frecuentes
1. ¿Como cambio la cuenta de estudiante que uso para obtener el horario?

    - R: Para actualizar las credenciales guardadas por la aplicacion, elimina el archivo "AulaCredentials.txt" del directorio donde se encuentra el programa. 

2. ¿Como importo mi horario a otra cuenta de Google? 

    - R: La aplicacion se conecta a la cuenta de Google que autorizaste la primera vez que corriste el programa y utiliza un token asociado a esa cuenta siempre que vuelves a utilizar la aplicacion. Para cambiar de cuenta de google, elmina el archivo 'token.pickle' del directorio donde se encuentra la aplicacion. 
  
## Instructions (English)

### Install

Requires python>=3.5

1. Download the repository on your PC/Mac from https://github.com/simonsanvil/GetHorarioDeClases.

2. Then use:
```
$ pip install -r requirements.txt
```
To install all the dependancies on your project.

### Use

1. Run the file "HorarioDeClases_app.py" in your console.
2. Follow the instruction in the console, the first time you are going to be prompted to introduce your NIA and Aula Global password. (This information never leaves your machine)
3. When required, sign into the Google account you wish to use the app with and accept the app permissions. This is only required to do one time.
4. Wait for the program to finish running and that's it! (might take a little while)


### Frequent questions

1. How to change the student account i use to get the calendar?

   - A: To update your Aula Global credentials, delete the file "AulaCredentials.txt" from the directory where the program is located.

2. How to import the calendar to another Google account?

   - A: The application connects to the Google account you authorized the first time the app was runned, and from then on, it uses a token associated to that google account everytime you run the application again. To change the Google account associated to the app all you have to do is delete the "token.pickle" file from the directory where the program is located.
