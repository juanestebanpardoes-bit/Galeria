"""
services.py  (versión v0.2.0)
-----------
Contiene las REGLAS del negocio.
NOVEDADES: agregar() recibe una prioridad y listar() puede ordenar por ella.
"""

from pathlib import Path

from models import Tarea, PRIORIDADES  # NUEVO: importamos también PRIORIDADES
import storage


class GestorTareas:
    """Administra la colección de tareas y la mantiene guardada en disco."""

    def __init__(self, ruta=storage.ARCHIVO_POR_DEFECTO):
        """Carga las tareas existentes al crear el gestor."""
        self._ruta = Path(ruta)
        self._tareas = storage.cargar_tareas(self._ruta)

    # ---------- Métodos privados (uso interno) ----------

    def _guardar(self) -> None:
        """Persiste el estado actual en el archivo."""
        storage.guardar_tareas(self._tareas, self._ruta)

    def _siguiente_id(self) -> int:
        """Calcula el próximo id: el mayor existente + 1 (o 1 si no hay tareas)."""
        return max((t.id for t in self._tareas), default=0) + 1

    def _buscar(self, id_tarea: int) -> Tarea:
        """Busca una tarea por id. Lanza LookupError si no existe."""
        for tarea in self._tareas:
            if tarea.id == id_tarea:
                return tarea
        raise LookupError(f"No existe una tarea con id {id_tarea}.")

    # ---------- Operaciones públicas ----------

    def agregar(self, titulo: str, prioridad: str = "media") -> Tarea:
        """Crea una tarea (HU-01 y HU-06).

        Lanza ValueError si el título está vacío o la prioridad no es válida.
        """
        titulo = titulo.strip()  # Quita espacios al inicio y al final
        if not titulo:
            raise ValueError("El título no puede estar vacío.")

        # NUEVO: normalizamos (minúsculas, sin espacios) y validamos la prioridad
        prioridad = prioridad.strip().lower()
        if prioridad not in PRIORIDADES:
            raise ValueError("La prioridad debe ser: " + ", ".join(PRIORIDADES) + ".")

        tarea = Tarea(id=self._siguiente_id(), titulo=titulo, prioridad=prioridad)
        self._tareas.append(tarea)
        self._guardar()
        return tarea

    def listar(self, solo_pendientes: bool = False,
               por_prioridad: bool = False) -> list[Tarea]:
        """Devuelve las tareas (HU-02 y RF-07).

        solo_pendientes: si es True, omite las completadas.
        por_prioridad:   si es True, ordena de alta a baja.
        """
        if solo_pendientes:
            tareas = [t for t in self._tareas if not t.completada]
        else:
            tareas = list(self._tareas)  # Copia, para no exponer la lista interna

        if por_prioridad:
            # La posición en PRIORIDADES define el orden: alta=0, media=1, baja=2.
            # sort() es estable: a igual prioridad se conserva el orden de creación.
            tareas.sort(key=lambda t: PRIORIDADES.index(t.prioridad))
        return tareas

    def completar(self, id_tarea: int) -> Tarea:
        """HU-03: marca una tarea como completada."""
        tarea = self._buscar(id_tarea)
        tarea.completada = True
        self._guardar()
        return tarea

    def eliminar(self, id_tarea: int) -> None:
        """HU-04: elimina una tarea por su id."""
        tarea = self._buscar(id_tarea)
        self._tareas.remove(tarea)
        self._guardar()
