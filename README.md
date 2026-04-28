# MotoTrack-DEMO-1
MotoTrack es una aplicación movil la cual permite gestionar el uso de motocicletas. Incluye registro de kilometraje, control de mantenimientos y un panel interactivo básico, mostrando cómo organizar y visualizar datos de forma práctica y sencilla.

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