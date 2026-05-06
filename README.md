# MotoTrack-DEMO-1

MotoTrack es una aplicaciÃ³n movil la cual permite gestionar el uso de motocicletas. Incluye registro de kilometraje, control de mantenimientos y un panel interactivo bÃ¡sico, mostrando cÃ³mo organizar y visualizar datos de forma prÃ¡ctica y sencilla.

## FUNCIONALIDADES PRINCIPALES DE ESTE ENTREGABLE

1. Registro de usuario
2. Gemeracion de alertas/Notificaciones
3. Sugerencias de cambio/Mantenimiento

## Estructura del proyecto

```text
mototrack/
├── app/                      # NÃºcleo de la aplicaciÃ³n
│   ├── database/             # ConfiguraciÃ³n y conexiÃ³n a la base de datos
│   │   ├── base.py
│   │   ├── engine.py
│   │   └── seed.py
│   ├── models/               # DefiniciÃ³n de entidades (tablas)
│   │   ├── alert.py
│   │   ├── maintenance.py
│   │   ├── motorcycle.py
│   │   └── user.py
│   ├── scheduler/            # Tareas automÃ¡ticas en segundo plano
│   │   └── jobs.py
│   ├── services/             # LÃ³gica de negocio
│   │   ├── alert_service.py
│   │   ├── auth_service.py
│   │   └── maintenance_service.py
│   └── state/                # Estado de la aplicaciÃ³n
│       └── session_state.py
├── ui/                       # Interfaz de usuario
│   ├── alerts/
│   ├── auth/
│   ├── maintenance/
│   └── shared/
├── tests/                    # Pruebas automatizadas
│   ├── test_alerts.py
│   ├── test_auth.py
│   └── test_maintenance.py
├── main.py                   # Punto de entrada
├── mototrack.db              # Base de datos SQLite
├── requirements.txt          #
```

## app/ â†’ NÃºcleo de la aplicaciÃ³n

### database/

Gestiona todo lo relacionado con la base de datos:

- base.py â†’ configuraciÃ³n base ORM
- engine.py â†’ conexiÃ³n a la base de datos
- seed.py â†’ datos iniciales para pruebas

### models/

Define la estructura de los datos:

- user.py â†’ usuarios
- motorcycle.py â†’ motocicletas
- maintenance.py â†’ mantenimientos
- alert.py â†’ alertas

AquÃ­ solo se define quÃ© datos existen, no la lÃ³gica.

### services/

Contiene la lÃ³gica del negocio:

- auth_service.py â†’ registro y autenticaciÃ³n
- maintenance_service.py â†’ gestiÃ³n de mantenimientos
- alert_service.py â†’ generaciÃ³n de alertas

AquÃ­ se implementan las reglas, validaciones y procesos.

### scheduler/

Automatiza tareas en segundo plano:

- jobs.py â†’ ejecuciÃ³n de procesos periÃ³dicos

Ejemplos:

- Revisar mantenimientos vencidos
- Generar alertas automÃ¡ticamente

### state/

Maneja el estado de la aplicaciÃ³n en tiempo de ejecuciÃ³n:

- session_state.py â†’ usuario activo y datos temporales

---

## ui/ â†’ Interfaz de usuario

Organizada por funcionalidades:

- auth/ â†’ pantallas de login y registro
- alerts/ â†’ visualizaciÃ³n de alertas
- maintenance/ â†’ gestiÃ³n de mantenimientos
- shared/ â†’ componentes reutilizables

---

## tests/ â†’ Pruebas

- test_auth.py
- test_alerts.py
- test_maintenance.py

Validan que la lÃ³gica funcione correctamente.

---

## Archivos principales

- main.py â†’ punto de entrada de la aplicaciÃ³n
- mototrack.db â†’ base de datos SQLite
- requirements.txt â†’ dependencias
- README.md â†’ documentaciÃ³n del proyecto
- .env â†’ variables de entorno

---

## Flujo de funcionamiento

1. El usuario se registra o inicia sesiÃ³n
2. Registra su motocicleta
3. Ingresa datos de uso (kilometraje)
4. El sistema:
   - EvalÃºa condiciones
   - Genera sugerencias
   - Programa alertas automÃ¡ticamente
5. El usuario recibe notificaciones y gestiona mantenimientos

---

## TecnologÃ­as utilizadas

- Python
- SQLite
- Arquitectura modular

---

## Escalabilidad del proyecto

MotoTrack estÃ¡ preparado para evolucionar hacia una arquitectura mÃ¡s robusta:

- MigraciÃ³n de la interfaz a Flutter
- ImplementaciÃ³n de backend con Flask
- IntegraciÃ³n con bases de datos en la nube
- Sistema de notificaciones en tiempo real
- API para integraciÃ³n con otras aplicaciones

---

## Estado del proyecto

VersiÃ³n DEMO funcional

Posibles mejoras:

- Notificaciones en tiempo real
- Dashboard avanzado
- IntegraciÃ³n con sensores o GPS
