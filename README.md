# Sistema de Gestion de Encomiendas

Proyecto Django para las sesiones de ORM y Django REST Framework. Usa PostgreSQL como unica base de datos persistente e incluye API versionada, JWT, Swagger, filtros, paginacion, throttling y tests automatizados.

## Requisitos

- Docker y Docker Compose
- Python 3.12 solo si quieres ejecutar comandos fuera del contenedor

## Inicio rapido

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

Accesos:

- App: `http://localhost:8000/`
- Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`
- API v1: `http://localhost:8000/api/v1/`
- API v2: `http://localhost:8000/api/v2/`

## Estructura

```text
config/      configuracion del proyecto
api/         serializers, viewsets, filtros, permisos, throttles y vistas DRF
clientes/    modelo y admin de clientes
rutas/       modelo y admin de rutas
envios/      empleados, encomiendas, historial, validators y querysets
```

## Variables de entorno

Archivo `.env` esperado:

```env
DEBUG=True
SECRET_KEY=change-me-before-production
ALLOWED_HOSTS=localhost,127.0.0.1,web
LANGUAGE_CODE=es-pe
TIME_ZONE=America/Lima
DB_ENGINE=django.db.backends.postgresql
DB_NAME=encomiendas_db
DB_USER=postgres
DB_PASSWORD=change-me
DB_HOST=db
DB_PORT=5432
DB_CONN_MAX_AGE=60
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000
```

## API DRF

Autenticacion JWT:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Endpoints principales:

- `GET|POST /api/v1/encomiendas/`
- `GET|PUT|PATCH|DELETE /api/v1/encomiendas/{id}/`
- `POST /api/v1/encomiendas/{id}/cambiar_estado/`
- `GET /api/v1/encomiendas/con_retraso/`
- `GET /api/v1/encomiendas/pendientes/`
- `GET /api/v1/encomiendas/estadisticas/`
- `POST /api/v1/encomiendas/bulk_create/`
- `PATCH /api/v1/encomiendas/bulk_estado/`
- `GET /api/v1/clientes/`
- `GET /api/v1/rutas/`

Endpoints demostrativos de fundamentos DRF:

- `GET|POST /api/v1/fundamentos/fbv/encomiendas/`
- `GET|POST /api/v1/fundamentos/apiview/encomiendas/`
- `GET|POST /api/v1/fundamentos/mixins/encomiendas/`
- `GET|POST /api/v1/fundamentos/generics/encomiendas/`

## Comandos utiles

```bash
docker compose up --build -d
docker compose down
docker compose logs -f web
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py test
docker compose exec web pytest
docker compose exec web python manage.py spectacular --validate --file schema.yml
docker compose exec web python manage.py shell
```

## Shell de demostracion

```python
from decimal import Decimal
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Empleado, Encomienda, HistorialEstado
from config.choices import EstadoEnvio, EstadoGeneral, TipoDocumento

hoy = timezone.localdate()

c1 = Cliente.objects.create(
    tipo_doc=TipoDocumento.DNI,
    nro_doc="12345678",
    nombres="Carlos",
    apellidos="Ramirez Torres",
    telefono="987654321",
    email="carlos@mail.com",
)

c2 = Cliente.objects.create(
    tipo_doc=TipoDocumento.DNI,
    nro_doc="87654321",
    nombres="Ana",
    apellidos="Flores Diaz",
)

r1 = Ruta.objects.create(
    codigo="LIM-TRU",
    origen="Lima",
    destino="Trujillo",
    precio_base=Decimal("25.00"),
    dias_entrega=2,
)

e1 = Empleado.objects.create(
    codigo="EMP001",
    nombres="Luis",
    apellidos="Mendoza Cruz",
    cargo="Operador de envios",
    email="luis@encomiendas.pe",
    fecha_ingreso=hoy,
)

enc = Encomienda.crear_con_costo_calculado(
    remitente=c1,
    destinatario=c2,
    ruta=r1,
    empleado=e1,
    descripcion="Caja con ropa y documentos",
    peso_kg=Decimal("3.50"),
)

enc.cambiar_estado(
    nuevo_estado=EstadoEnvio.EN_TRANSITO,
    empleado=e1,
    observacion="Encomienda recogida en agencia Lima",
)

HistorialEstado.objects.filter(encomienda=enc)
Encomienda.objects.pendientes()
Encomienda.objects.activas().por_ruta(r1).count()
Cliente.objects.activos()
Cliente.objects.buscar("Ramirez")

try:
    Encomienda.objects.create(
        codigo="MAL-001",
        descripcion="Prueba invalida",
        peso_kg=Decimal("-1.00"),
        remitente=c1,
        destinatario=c1,
        ruta=r1,
        empleado_registro=e1,
        costo_envio=Decimal("0.00"),
        fecha_entrega_est=hoy - timedelta(days=1),
    )
except ValidationError as exc:
    print(exc.message_dict)
```

## Notas de desarrollo

- El contenedor `web` espera a PostgreSQL y aplica migraciones automaticamente al iniciar.
- El endpoint `/api/v1/encomiendas/estadisticas/` usa cache local en memoria durante 15 minutos; los datos del sistema se guardan solo en PostgreSQL.
- El proyecto esta orientado a desarrollo y demostracion, no a produccion.
