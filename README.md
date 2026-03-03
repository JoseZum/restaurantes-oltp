# Restaurantes API - Sistema Transaccional (OLTP)

API REST para gestion de restaurantes construida con Node.js, Express y soporte dual de base de datos (PostgreSQL y MongoDB con sharding). Incluye cache con Redis, busqueda full-text con Elasticsearch, balanceo de carga con Nginx y pipeline CI/CD con GitHub Actions.

---

## Arquitectura

```
Cliente HTTP
    |
    v
  Nginx (puerto 80)
    |
    +---> API REST (Express, puerto 3000)
    |         |
    |         +---> PostgreSQL / MongoDB
    |         +---> Redis (cache)
    |
    +---> Search Service (puerto 4000)
              |
              +---> Elasticsearch
```

---

## Prerrequisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo local sin Docker)
- Git

---

## Configuracion

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd restaurantes-oltp
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar el archivo `.env` segun sea necesario. La variable `DB_ENGINE` controla cual base de datos se utiliza:

```env
# Usar PostgreSQL
DB_ENGINE=postgres

# O usar MongoDB
DB_ENGINE=mongo
```

**Nota:** Solo debe haber un motor de base de datos activo a la vez.

---

## Despliegue con Docker Compose

### Opcion 1: Imagen desde GitHub Container Registry

```bash
docker pull ghcr.io/ianporras17/restaurantes-api:latest
docker compose up -d
```

### Opcion 2: Build local (desarrollo)

```bash
# Si se usa MongoDB, levantar primero el cluster
docker compose -f mongo-cluster/docker-compose.mongo.yml up -d
# Esperar al menos 2 minutos para la replicacion y sharding

# Levantar el resto del sistema
docker compose up -d
```

### Verificar que los servicios estan corriendo

```bash
docker compose ps
```

---

## Servicios y Puertos

| Servicio         | Puerto | Descripcion                        |
|------------------|--------|------------------------------------|
| Nginx            | 80     | Punto de entrada principal         |
| API REST         | 3000   | Servidor Express                   |
| Search Service   | 4000   | Microservicio de busqueda          |
| PostgreSQL       | 5437   | Base de datos relacional           |
| PgAdmin          | 5050   | Administracion de PostgreSQL       |
| Elasticsearch    | 9206   | Motor de busqueda                  |
| Redis            | 6379   | Cache en memoria                   |

---

## Endpoints de la API

Todas las rutas se acceden a traves de Nginx en `http://localhost`.

### Autenticacion

| Metodo | Ruta           | Descripcion                     |
|--------|----------------|---------------------------------|
| POST   | /auth/register | Registro de nuevo usuario       |
| POST   | /auth/login    | Login (retorna token JWT)       |

### Usuarios

| Metodo | Ruta       | Descripcion            |
|--------|------------|------------------------|
| GET    | /users/me  | Obtener perfil propio  |
| PUT    | /users/:id | Actualizar usuario     |
| DELETE | /users/:id | Eliminar usuario       |

### Restaurantes

| Metodo | Ruta          | Descripcion           |
|--------|---------------|-----------------------|
| POST   | /restaurants  | Crear restaurante     |
| GET    | /restaurants  | Listar restaurantes   |

### Menus

| Metodo | Ruta       | Descripcion         |
|--------|------------|---------------------|
| POST   | /menus     | Crear menu          |
| GET    | /menus/:id | Obtener menu por ID |
| PUT    | /menus/:id | Actualizar menu     |
| DELETE | /menus/:id | Eliminar menu       |

### Reservaciones

| Metodo | Ruta              | Descripcion          |
|--------|-------------------|----------------------|
| POST   | /reservations     | Crear reservacion    |
| DELETE | /reservations/:id | Cancelar reservacion |

### Pedidos

| Metodo | Ruta       | Descripcion           |
|--------|------------|-----------------------|
| POST   | /orders    | Crear pedido          |
| GET    | /orders/:id| Obtener pedido por ID |

### Busqueda (Elasticsearch)

| Metodo | Ruta                         | Descripcion             |
|--------|------------------------------|-------------------------|
| GET    | /search/products?q=texto     | Busqueda full-text      |
| GET    | /search/products/category/:c | Buscar por categoria    |
| POST   | /search/reindex              | Reindexar datos         |

---

## Cache con Redis

Redis se utiliza automaticamente para cachear las siguientes consultas:

- `GET /menus/:id` - Menus por ID
- `GET /orders/:id` - Pedidos por ID

La primera consulta accede a la base de datos; las siguientes se sirven desde cache. Para inspeccionar las claves almacenadas:

```bash
docker exec -it redis redis-cli KEYS *
```

---

## Balanceo de Carga - Nginx

Nginx actua como reverse proxy y enruta las peticiones:

| Patron de ruta | Servicio destino              |
|----------------|-------------------------------|
| /search/*      | search-service (puerto 4000)  |
| Todo lo demas  | restaurantes-api (puerto 3000)|

---

## MongoDB - Replicacion y Sharding

Si se utiliza MongoDB como motor de base de datos:

```bash
# Ver estado del sharding
docker exec -it mongos mongosh --host mongos --eval "sh.status()"

# Ver estado de la replicacion
docker exec -it mongo1 mongosh --eval "rs.status()"
```

---

## Cambiar entre PostgreSQL y MongoDB

```bash
# Detener contenedores
docker compose down

# Editar .env
DB_ENGINE=mongo   # o postgres

# Levantar de nuevo
docker compose up -d
```

---

## Pruebas

```bash
npm run test
```

La suite de pruebas ejecuta:
- `test:pg` - Pruebas con PostgreSQL
- `test:mongo` - Pruebas con MongoDB
- Genera reporte de cobertura automaticamente

---

## Despliegue en Kubernetes

Los manifiestos de Kubernetes se encuentran en el directorio `k8s/`:

```bash
# Crear namespace
kubectl apply -f k8s/namespace.yaml

# Configuracion
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Base de datos
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml

# Cache
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
```

---

## CI/CD con GitHub Actions

El pipeline se activa automaticamente al hacer push a la rama `main`. Se puede verificar en la pestana "Actions" del repositorio en GitHub.

---

## Estructura del Proyecto

```
restaurantes-oltp/
|-- src/
|   |-- modules/
|   |   |-- users/          # Autenticacion y gestion de usuarios
|   |   |-- restaurants/    # CRUD de restaurantes
|   |   |-- menus/          # CRUD de menus
|   |   |-- orders/         # Gestion de pedidos
|   |   +-- reservations/   # Gestion de reservaciones
|   |-- search/             # Microservicio de busqueda (Elasticsearch)
|   |-- db/                 # Adaptadores de base de datos
|   |-- middlewares/        # JWT, validacion
|   |-- utils/              # Utilidades compartidas
|   |-- routes.js           # Definicion de rutas
|   |-- app.js              # Configuracion de Express
|   +-- index.js            # Punto de entrada
|-- tests/                  # Suite de pruebas (Jest)
|-- mongo-cluster/          # Configuracion de sharding MongoDB
|-- nginx/                  # Configuracion de Nginx
|-- k8s/                    # Manifiestos de Kubernetes
|-- docker-compose.yml      # Configuracion Docker Compose
|-- Dockerfile              # Imagen Docker de la API
+-- package.json            # Dependencias y scripts
```
