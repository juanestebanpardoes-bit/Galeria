# Gestor de Tareas

Aplicación de consola para administrar tareas pendientes (MVP v0.1.0).

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
