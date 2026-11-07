# Gestor de Tareas

Aplicación de consola para administrar tareas pendientes (v0.2.0).

## Requisitos
- Python 3.10 o superior

## Ejecución
```bash
python main.py
```

## Pruebas
```bash
python -m unittest -v
```

## Funcionalidades
- Agregar, listar, completar y eliminar tareas
- Prioridad (alta, media, baja) y orden por prioridad
- Las tareas se guardan en `tareas.json`

## Autores
- Nombre 1
- Nombre 2

## Estructura
- `main.py`: interfaz de consola
- `services.py`: lógica de negocio
- `storage.py`: persistencia JSON
- `models.py`: modelo de datos
- `test_services.py`: pruebas unitarias
