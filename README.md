# Example App


# Feature:
- FastAPI: Backend
- MySQL: Database
- Alembic: Database Migrations
- Poetry: Requirement Control


## Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.

## Local development

1. Create new .env file and change it
    ```bash
    cp .env.example .env
    ```
   Next change .env configs, generate new secret key with command
    ```bash
    make generate-secret
    ```


2. Start Infra
    ```bash
    docker-compose up -d
    ```


3. Start FastAPI App
    ```bash
    make start-app
    ```



### Now you can open your browser and interact with these URLs:

* JSON based web API based on OpenAPI: http://localhost:8000/api/

* Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://localhost:8000/docs

* Alternative automatic documentation with ReDoc (from the OpenAPI backend): http://localhost:8000/redoc
