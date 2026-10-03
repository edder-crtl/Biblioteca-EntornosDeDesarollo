Sistema de Gestión de Biblioteca

Este proyecto es una solución integral para la administración y control de operaciones de una biblioteca. Permite gestionar de forma eficiente el catálogo de libros, los usuarios registrados y los préstamos o devoluciones dentro del sistema.

Tabla de Contenidos

Visión General

Arquitectura y Tecnologías

Backend

Frontend

Estructura del Proyecto

Endpoints Principales de la API

Requisitos Previos

Guía de Instalación y Ejecución

1. Configuración del Backend

2. Ejecución del Frontend

Licencia

Visión General

El Sistema de Gestión de Biblioteca simplifica las tareas administrativas mediante un panel interactivo que interactúa en tiempo real con una API RESTful. La aplicación implementa operaciones CRUD completas para libros y usuarios, además de gestionar las reglas de negocio vinculadas al préstamo de ejemplares.

Arquitectura y Tecnologías

Backend

Framework: FastAPI

ORM: SQLAlchemy

Base de Datos: SQLite (ligera y autocontenida)

Validación de Datos: Pydantic

Servidor ASGI: Uvicorn

Frontend

Estructura: HTML5

Estilos: CSS3 (diseño modular y responsivo)

Lógica: JavaScript Vanilla (ES6+)

Comunicación HTTP: Fetch API (consumo asíncrono de endpoints)

Estructura del Proyecto

sistema-biblioteca/
├── backend/
│   ├── app/
│   │   ├── database.py       # Configuración y conexión de SQLAlchemy
│   │   ├── models.py         # Modelos de tablas de la base de datos
│   │   ├── schemas.py        # Esquemas de validación de Pydantic
│   │   ├── crud.py           # Operaciones directas a la base de datos
│   │   └── main.py           # Punto de entrada de FastAPI y rutas
│   ├── requirements.txt      # Dependencias del proyecto Python
│   └── biblioteca.db         # Archivo de base de datos SQLite (generado automáticamente)
│
└── frontend/
    ├── css/
    │   └── styles.css        # Hoja de estilos global
    ├── js/
    │   ├── api.js            # Funciones modularizadas con Fetch API
    │   └── app.js            # Manejo del DOM y eventos
    └── index.html            # Interfaz principal de usuario


Endpoints Principales de la API

La documentación interactiva e interactiva mediante Swagger UI está disponible automáticamente en http://127.0.0.1:8000/docs al iniciar el servidor.

Libros (/books)

GET /books/ - Obtener la lista completa de libros.

GET /books/{id} - Obtener información detallada de un libro por su ID.

POST /books/ - Registrar un nuevo libro en el catálogo.

PUT /books/{id} - Actualizar la información de un libro.

DELETE /books/{id} - Eliminar un libro existente.

Usuarios (/users)

GET /users/ - Consultar todos los usuarios registrados.

GET /users/{id} - Consultar un usuario específico.

POST /users/ - Crear una nueva cuenta de usuario.

DELETE /users/{id} - Dar de baja a un usuario.

Préstamos (/loans)

GET /loans/ - Listar el historial de préstamos.

POST /loans/ - Registrar el préstamo de un libro a un usuario.

PUT /loans/{id}/return - Marcar la devolución de un libro prestado.

Requisitos Previos

Asegúrate de contar con los siguientes elementos instalados en tu sistema:

Python 3.8 o superior

Un navegador web moderno (Chrome, Firefox, Edge o Safari)

Git (opcional, para clonar el repositorio)

Guía de Instalación y Ejecución

1. Configuración del Backend

Navegar al directorio backend:

cd backend


Crear un entorno virtual:

python -m venv venv


Activar el entorno virtual:

En Linux/macOS:

source venv/bin/activate


En Windows:

venv\Scripts\activate


Instalar las dependencias:

pip install -r requirements.txt


Iniciar el servidor backend:

uvicorn app.main:app --reload


El backend estará ejecutándose en http://127.0.0.1:8000.

2. Ejecución del Frontend

Dado que la capa cliente fue desarrollada con HTML, CSS y JavaScript Vanilla, no requiere un proceso de compilación.

Navega a la carpeta frontend/.

Abre el archivo index.html en tu navegador web preferido o utilízalo a través de una extensión de servidor local como Live Server en VS Code.

Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
