# MotoTrack Demo

MotoTrack es una aplicacion de escritorio construida con Flet para gestionar motocicletas, mantenimientos y alertas. El proyecto usa SQLite + SQLAlchemy y esta organizado por capas para separar datos, logica y UI.

## Funcionalidades

1. Registro e inicio de sesión de usuarios.
2. Registro de motocicletas por usuario.
3. Historial de mantenimientos.
4. Alertas por kilometraje o fecha.
5. Sugerencias visibles en el panel segun el estado actual de la moto.

## Estructura del proyecto

```text
PGC 3/
|-- app/
|   |-- database/
|   |-- models/
|   |-- scheduler/
|   |-- services/
|   `-- state/
|-- tests/
|-- ui/
|   |-- alerts/
|   |-- auth/
|   |-- maintenance/
|   `-- shared/
|-- main.py
|-- requirements.txt
|-- pyrightconfig.json
`-- README.md
```

## Capas

### `app/database`

- `base.py`: base ORM.
- `engine.py`: conexión, sesiones e inicialización.
- `seed.py`: datos demo opcionales.

### `app/models`

- `user.py`: usuarios.
- `motorcycle.py`: motocicletas.
- `maintenance.py`: mantenimientos.
- `alert.py`: alertas.

### `app/services`

- `auth_service.py`: registro, login y motocicletas del usuario.
- `maintenance_service.py`: creacion y consulta de mantenimientos.
- `alert_service.py`: creacion, consulta y evaluacion de alertas.

### `app/state`

- `session_state.py`: estado del usuario autenticado en la UI.

### `ui`

- `auth/`: login, registro y resumen visual del usuario.
- `maintenance/`: detalle de moto, sugerencias, formulario e historial.
- `alerts/`: formulario y listado de alertas.
- `shared/`: tema, navbar y snackbar reutilizables.

## Ejecucion

### 1. Crear entorno e instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Iniciar la app

```powershell
.\.venv\Scripts\python.exe main.py
```

Si `AUTO_SEED_DATA=true` en `.env`, podras entrar con:

```text
demo@mototrack.local / demo1234
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Despliegue

El entrypoint es `main.py`. En servidores web define estas variables:

```text
FLET_WEB=true
PORT=8550
AUTO_SEED_DATA=false
MOTOTRACK_DB_URL=sqlite:///mototrack.db
```

En plataformas tipo Render/Heroku puedes usar el `Procfile` incluido:

```text
web: python main.py
```

## Estado actual

- Backend funcional y probado.
- UI modularizada por dominio.
- Estructura duplicada antigua eliminada.

## Mejoras futuras

- Notificaciones reales en segundo plano.
- API HTTP para integracion externa.
- Edicion y eliminacion de alertas y mantenimientos desde la UI.
