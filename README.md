# DSV-Proyecto
Simulación de los procedimientos de seguimiento de la Inscripción y Enajenación de bienes raíces, con el objeto de poder determinar quienes son los propietarios de un bien raíz y en qué proporción, en un determinado momento.

## Entrega 2
Para la 2ª parte del proyecto, se implementará la carga de datos en la Multipropietario a través del procesamiento de los F2890 ingresados.

### Se asume
- Todos los datos de los formularios vienen bien: no hay enajenantes fantasma (que no existan), no hay formularios con porcentajes negativos o que superen el 100% de la propiedad. 
- Si el formulario viene con algún dato incorrecto, se pide almacenar los datos pero no se procesa.

### Conceptos que se revisaran
- Meaningful Names. Specifically, the following aspects will be taken into consideration:
  * Intention-revealing names.
  * Avoid disinformation.
  * Make meaningfull distinctions.
  * Use pronounceable names.
  * Use searchable names. No magic constants
  * Avoid encodings.
  * Avoid a personal mental mapping.
  * Name correctly your classes.
  * Name correctly your methods.
  * Do not try to be cute.
  * Pick one word per concept.
  * Do not pun.
  * Use solution domain names.
  * Use problem domain names.
  * Add meaningful context.
  * Don’t add gratuitous context.
- Coding Standard. The application of the standard for C# provided in in this course. The subcategories being considered are:
  * Naming conventions
  * Coding style
  * Language usage
- Comments. The correct use of comments in your code. Neither we are saying you must put
comments in your code, nor that it is bad to use them; you must decide when they are useful and necessary.
- Functions. The following subcategories will be considered:
  * Naming. In addition to the correct application of the standard, they must follow the guidelines presented in class
  * Size
  * One level of abstraction
  * The application of the stepdown rule (the newspaper metaphor)
  * Number and use of arguments
  * No side effect
  * Separation of command and query
  * Good use of exceptions vs return codes
  * Dummy scopes and switch statements
  * Don’t repeat yourself
- Formatting. The following subcategories will be considered:
  * Vertical openness between concepts
  * Vertical density
  * Vertical distance
  * Vertical ordering
  * Horizontal openness and density
  * Good horizontal alignment
  * Indentation
- Objects vs Data structure
  * The correct level of visibility for each of the objects

### Algoritmo
#### Regularización de patrimonio (99)
- Escenario 1: No hay historial del predio
  No hay historial del predio, por lo tanto se hace lo siguiente:
	* Instrucciones profe
	  - Se agregan todos los datos del formulario
	* Que deberiamos hacer
	  - Se agregan todos los datos del formulario

- Escenario 2: Llega un formulario nuevo
	Llega un formulario cuando ya existen registros del predio.
	* Instrucciones profe
	  - Acotar registros previos
	  - Agregar nuevo registro
	* Que deberiamos hacer
	  - Guardar nuevo registro

- Escenario 3: Llega un formulario antiguo
	Llega un formulario antiguo cuando ya existen registros del predio.
	* Instrucciones profe
	  - Borrar de multipropietario los registros posteriores al que esta siendo agregado
	  - Reprocesar formularios en orden cronologico
	* Que deberiamos hacer
	  - Opción 1:
		* Guardar temporalmente los datos de todos los registros
		* Cambiar los datos del primer registro al nuevo que esta siendo ingresado
		* Reasignar los valores de cada registro a uno posterior
		* El ultimo (más nuevo) es un nuevo registro
	  - Opción 2:
		* Guardar como nuevo registro, como ya tiene año, no es necesario reasignar los registros, solo que al hacer la query se ordene por año.

- Escenario 4: Llega un formulario para el mismo año
Llega un formulario antiguo cuando ya existen registros del predio.
	* Instrucciones profe
	  - Borrar de multipropietario los registros afectados

## Evaluación
La evaluación funcional considera lo que se vio en la parte 1, es decir el correcto funcionamiento de todas las pantallas y la carga de JSON, solo que ahora la Multipropietario se llena con el procesamiento de los F2890. Especial atención se dará a la implementación del algoritmo y los resultados almacenados en la Multipropietario.

Como en la entrega 1, se rechazarán aquellos proyectos con fallas funcionales críticas y para las no críticas, se descontará 0,5 puntos por cada una de ellas.

También se rechazarán aquellas entregas con fallas técnicas críticas, es decir, que no cumplan con la funcionalidad básica solicitada en términos de persistir y mostrar los datos ingresados y/o que presenten situaciones de error.

For each problem encountered in the different sub-categories, points will be deducted from your grade according to the following table:
- 0,5 for first problem
- 0,3 for second problem
- 0,2 for third problem
- 0,1 for fourth problem and followings
A maximum of 1,5 points will be deducted for each subcategory. The minimum grade is, of course, 1,0.

## Prequisites
Podman o docker instalado en el sistema

## Getting Started
### Database Setup

  - Pull the MySQL Docker image:
    ```bash
    podman pull docker.io/mysql
    ```

  - Run the MySQL container:
    ```bash
    podman run --name mysql -e MYSQL_ROOT_PASSWORD={db_password} -p 3306:3306 -d mysql
    ```

  - Access the MySQL container and create the database:
    ```bash
    mysql -uroot -p{db_password}
    create database {db_name};
    ```

### Application Setup

  - Create a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
  - Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
  - Create a .env file and fill in the following details:
    ```txt
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD={db_password}
    DB_NAME={db_name}
    APP_SECRET=secret
    FLASK_ENV=development
    ```

### Run app
  - Populate database and run app
  ```bash
  flask --app flaskr populate-db
  flask --app flaskr run
  ```
