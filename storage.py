"""
storage.py
----------
Se encarga exclusivamente de LEER y ESCRIBIR tareas en un archivo JSON.
No contiene reglas de negocio ni interacción con el usuario.
"""

import json
from pathlib import Path

from models import Tarea

# Archivo donde se guardan las tareas (se crea en la carpeta del proyecto)
ARCHIVO_POR_DEFECTO = Path("tareas.json")


def cargar_tareas(ruta=ARCHIVO_POR_DEFECTO) -> list[Tarea]:
    """Lee las tareas del archivo JSON.

    Si el archivo no existe (primera ejecución) devuelve una lista vacía.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    with ruta.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)  # Lista de diccionarios
    return [Tarea.desde_diccionario(d) for d in datos]


def guardar_tareas(tareas: list[Tarea], ruta=ARCHIVO_POR_DEFECTO) -> None:
    """Escribe todas las tareas en el archivo JSON (reemplaza el contenido)."""
    ruta = Path(ruta)
    with ruta.open("w", encoding="utf-8") as archivo:
        # ensure_ascii=False conserva tildes y ñ; indent=2 lo hace legible
        json.dump([t.a_diccionario() for t in tareas], archivo,
                  ensure_ascii=False, indent=2)
