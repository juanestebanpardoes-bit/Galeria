# Gestor de Tareas

Aplicación de consola para administrar tareas pendientes (v0.3.0).

## Requisitos
- Python 3.10 o superior

## Ejecución
Versión con ventanas (recomendada):
```bash
python gui.py
```
Versión de consola:
```bash
python main.py
```

En Linux, si falta tkinter: `sudo apt install python3-tk`.

## Pruebas
```bash
python -m unittest -v
```

## Funcionalidades
- Agregar, listar, completar y eliminar tareas
- Prioridad (alta, media, baja) y orden por prioridad
- Interfaz gráfica: editar, filtrar, buscar, barra de progreso, fuente Comic Sans y fondo azul celeste con texto negro
- Recordatorios por tarea: desde el botón **Recordatorio** se puede elegir el día,
  la semana o el mes siguiente; las alertas aparecen mientras la aplicación está abierta
- Las tareas se guardan en `tareas.json`

## Autores
- Nombre 1
- Nombre 2

## Estructura
- `gui.py`: interfaz gráfica con ventanas (tkinter)
- `main.py`: interfaz de consola
- `services.py`: lógica de negocio
- `storage.py`: persistencia JSON
- `models.py`: modelo de datos
- `test_services.py`: pruebas unitarias
