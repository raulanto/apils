
<div align="center">
  <img src="icon.svg" alt="Gestor de Gastos Personales Logo" width="150" />
  <h1>APILS - Backend Estandarizado (FastAPI/Python)</h1>
  <p><em><a href="https://github.com/raulanto">raulanto</a></em></p>
</div>


Backend para el proyecto APILS, desarrollado con FastAPI y Python moderno.

## Arquitectura

El proyecto sigue un enfoque modular inspirado en **Clean Architecture** (Arquitectura Limpia) y principios de **Domain-Driven Design (DDD)**. 

### ¿Por qué esta arquitectura?

El objetivo principal de esta estructura es la **Separación de Responsabilidades (Separation of Concerns)**. Al dividir el código en capas independientes, logramos:

1. **Mantenibilidad y Escalabilidad**: A medida que el proyecto crece, es fácil saber exactamente dónde colocar nueva lógica. Evita el antipatrón de tener archivos gigantes y desordenados ("Big Ball of Mud").
2. **Independencia del Framework y Base de Datos**: Las reglas de negocio centrales están aisladas. Si en el futuro se necesita cambiar el framework web (FastAPI) o el ORM (SQLAlchemy), el impacto en la lógica de negocio será mínimo.
3. **Testabilidad**: Al estar la infraestructura separada del dominio, es mucho más sencillo escribir pruebas unitarias. Podemos simular (mockear) la base de datos o servicios externos fácilmente para probar la lógica de negocio de forma aislada y rápida.
4. **Reusabilidad**: Los componentes pueden ser reutilizados fácilmente gracias al uso intensivo del patrón de Inyección de Dependencias.

### Estructura de Capas

El código fuente principal se encuentra dentro del directorio `src/apils` y se divide en las siguientes capas (desde la interfaz externa hasta el núcleo):

- **`api/`** *(Capa de Presentación)*: Contiene los enrutadores (routers) y endpoints de FastAPI. Su única responsabilidad es recibir peticiones HTTP, delegar el procesamiento a las capas internas y devolver respuestas HTTP. No debe contener lógica de negocio compleja.
- **`schemas/`** *(Capa de Presentación / Aplicación)*: Modelos de Pydantic (Data Transfer Objects o DTOs). Definen la estructura estricta de los datos que entran (Requests) y salen (Responses) de la API, encargándose de la validación inicial de los tipos de datos.
- **`dependencies/`** *(Capa de Aplicación)*: Aprovecha el sistema de Inyección de Dependencias de FastAPI. Aquí se instancian y proveen componentes reutilizables (ej. la sesión de la base de datos, repositorios, o la verificación del usuario autenticado actual).
- **`core/`** *(Capa Transversal)*: Configuraciones globales de la aplicación, manejo de variables de entorno (`settings`), seguridad (hashing, tokens JWT) y utilidades compartidas que se usan a lo largo de todo el proyecto.
- **`infrastructure/`** *(Capa de Infraestructura)*: Alberga los detalles técnicos y las interacciones con sistemas externos. Incluye los modelos ORM de SQLAlchemy (que mapean las tablas de la base de datos), y las implementaciones de repositorios que realizan consultas SQL reales.
- **`domain/`** *(Capa de Dominio - El Núcleo)*: El corazón del sistema. Contiene las entidades puras del dominio, enumeradores y las reglas de negocio más importantes. Esta capa **no debe depender** de frameworks externos (idealmente ni de FastAPI ni de SQLAlchemy). El resto del código existe para servir a este dominio.
- **`main.py`** *(Composition Root)*: Punto de entrada central de la aplicación. Es donde se inicializa la instancia de FastAPI, se configuran middlewares, CORS y se registran los routers.

## Tecnologías Principales

- **Framework Web**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM y Base de Datos**: [SQLAlchemy](https://www.sqlalchemy.org/) 2.0+ (soporte asíncrono para SQLite/PostgreSQL)
- **Migraciones**: [Alembic](https://alembic.sqlalchemy.org/)
- **Autenticación**: FastAPI-Users
- **Gestión de Paquetes**: [uv](https://docs.astral.sh/uv/)

## Configuración y Puesta en Marcha

### Prerrequisitos

- Python 3.14 o superior.
- El gestor de paquetes **uv** instalado.

### Instalación Local

1. **Instalar las dependencias y preparar el entorno virtual**:
   Ejecuta el siguiente comando para sincronizar las dependencias listadas en el `pyproject.toml` usando `uv`:

   ```bash
   uv sync
   ```

2. **Variables de Entorno**:
   Asegúrate de configurar correctamente el archivo `.env` en la raíz del proyecto. Este archivo debe contener al menos la URL de conexión a la base de datos (por defecto configurado para usar `test.db`).

3. **Ejecutar las Migraciones**:
   Antes de iniciar la aplicación, aplica las migraciones de Alembic para crear las tablas necesarias en la base de datos:

   ```bash
   uv run alembic upgrade head
   ```

4. **Iniciar el Servidor**:
   Puedes arrancar el servidor en modo desarrollo utilizando el script configurado en el proyecto:
   ```bash
   uv run apils
   ```
   ```bash
   uv run uvicorn apils.main:app --reload
   ```
   O de forma equivalente usando el CLI de FastAPI:
   ```bash
   uv run fastapi dev src/apils/main.py
   ```

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva de la API (Swagger UI) en:
[http://localhost:8000/docs](http://localhost:8000/docs)
