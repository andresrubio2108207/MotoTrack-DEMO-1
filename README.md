# MotoTrack-DEMO-1
MotoTrack es una aplicación movil la cual permite gestionar el uso de motocicletas. Incluye registro de kilometraje, control de mantenimientos y un panel interactivo básico, mostrando cómo organizar y visualizar datos de forma práctica y sencilla.

# FUNCIONALIDADES PRINCIPALES DE ESTE ENTREGABLE:

1 Registro de usuario
2 Gemeracion de alertas/Notificaciones 
3 Sugerencias de cambio/Mantenimiento

# ESTRUCTURA DEL PROYECTO

mototrack/
├── app/
│   ├── database/
│   │   ├── base.py
│   │   ├── engine.py
│   │   └── seed.py
│   │
│   ├── models/
│   │   ├── alert.py
│   │   ├── maintenance.py
│   │   ├── motorcycle.py
│   │   └── user.py
│   │
│   ├── scheduler/
│   │   └── jobs.py
│   │
│   ├── services/
│   │   ├── alert_service.py
│   │   ├── auth_service.py
│   │   └── maintenance_service.py
│   │
│   └── state/
│       └── session_state.py
│
├── ui/
│   ├── alerts/
│   ├── auth/
│   ├── maintenance/
│   └── shared/
│
├── tests/
│   ├── test_alerts.py
│   ├── test_auth.py
│   └── test_maintenance.py
│
├── main.py
├── mototrack.db
├── requirements.txt
├── README.md
└── .env


## app/ → Núcleo de la aplicación

### database/
Gestiona todo lo relacionado con la base de datos:
- base.py → configuración base ORM
- engine.py → conexión a la base de datos
- seed.py → datos iniciales para pruebas

### models/
Define la estructura de los datos:
- user.py → usuarios
- motorcycle.py → motocicletas
- maintenance.py → mantenimientos
- alert.py → alertas

Aquí solo se define qué datos existen, no la lógica.

### services/
Contiene la lógica del negocio:
- auth_service.py → registro y autenticación
- maintenance_service.py → gestión de mantenimientos
- alert_service.py → generación de alertas

Aquí se implementan las reglas, validaciones y procesos.

### scheduler/
Automatiza tareas en segundo plano:
- jobs.py → ejecución de procesos periódicos

Ejemplos:
- Revisar mantenimientos vencidos
- Generar alertas automáticamente

### state/
Maneja el estado de la aplicación en tiempo de ejecución:
- session_state.py → usuario activo y datos temporales

---

## ui/ → Interfaz de usuario

Organizada por funcionalidades:
- auth/ → pantallas de login y registro
- alerts/ → visualización de alertas
- maintenance/ → gestión de mantenimientos
- shared/ → componentes reutilizables

---

## tests/ → Pruebas

- test_auth.py
- test_alerts.py
- test_maintenance.py

Validan que la lógica funcione correctamente.

---

# Archivos principales

- main.py → punto de entrada de la aplicación
- mototrack.db → base de datos SQLite
- requirements.txt → dependencias
- README.md → documentación del proyecto
- .env → variables de entorno

---

# Flujo de funcionamiento

1. El usuario se registra o inicia sesión  
2. Registra su motocicleta  
3. Ingresa datos de uso (kilometraje)  
4. El sistema:
   - Evalúa condiciones
   - Genera sugerencias
   - Programa alertas automáticamente  
5. El usuario recibe notificaciones y gestiona mantenimientos  

---

# Tecnologías utilizadas

- Python
- SQLite
- Arquitectura modular

---

# Escalabilidad del proyecto

MotoTrack está preparado para evolucionar hacia una arquitectura más robusta:

- Migración de la interfaz a Flutter
- Implementación de backend con Flask
- Integración con bases de datos en la nube
- Sistema de notificaciones en tiempo real
- API para integración con otras aplicaciones

---

# Estado del proyecto

Versión DEMO funcional

Posibles mejoras:
- Notificaciones en tiempo real
- Dashboard avanzado
- Integración con sensores o GPS