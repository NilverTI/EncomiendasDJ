# Sistema de Gestión de Encomiendas

Aplicación Django para gestionar envíos, clientes y rutas de entrega con PostgreSQL y Docker.

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# 1. Clonar y configurar
git clone <repository-url>
cd encomiendas
cp .env.example .env

# 2. Iniciar servicios
docker-compose up

# 3. Acceder
# Aplicación: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### Sin Docker

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 📋 Modelos

| Modelo | Descripción | Campos Clave |
|--------|-------------|--------------|
| **Cliente** | Información de clientes | nombre, email (único), teléfono, dirección, activo |
| **Ruta** | Rutas de entrega | código, origen, destino, distancia, estado |
| **Encomienda** | Envíos/paquetes | numero_seguimiento, cliente (FK), ruta (FK), estado, valor |

## 🔧 Stack Tecnológico

- **Backend:** Django 6.0.4
- **Database:** PostgreSQL 15
- **Python:** 3.12
- **Containerización:** Docker + Docker Compose
- **WSGI:** Gunicorn

## 📁 Estructura del Proyecto

```
encomiendas/
├── clientes/          # Gestión de clientes
├── envios/            # Gestión de envíos
├── rutas/             # Gestión de rutas
├── config/            # Configuración Django
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```
DEBUG=True
SECRET_KEY=<tu-clave-secreta>
ALLOWED_HOSTS=localhost,127.0.0.1,web
DB_ENGINE=django.db.backends.postgresql
DB_NAME=encomiendas_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

## 📝 Comandos Útiles

```bash
# Docker
docker-compose up              # Iniciar
docker-compose down            # Detener
docker-compose logs -f web     # Ver logs

# Django
python manage.py migrate              # Aplicar migraciones
python manage.py createsuperuser      # Crear admin
python manage.py shell                # Shell interactivo
```

## ⚠️ Seguridad en Producción

- [ ] Cambiar `SECRET_KEY`
- [ ] Establecer `DEBUG=False`
- [ ] Cambiar contraseñas por defecto
- [ ] Usar HTTPS
- [ ] Configurar ALLOWED_HOSTS

## 📄 Licencia

Este proyecto es de código abierto.
