"""
services.py
-----------
Contiene las REGLAS del negocio: qué se puede hacer con las tareas y qué
validaciones se aplican. No imprime ni pide datos al usuario (eso es de main.py).
"""

from pathlib import Path

from models import Tarea
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

    # ---------- Operaciones públicas (HU-01 a HU-04) ----------

    def agregar(self, titulo: str) -> Tarea:
        """HU-01: crea una tarea. Lanza ValueError si el título está vacío."""
        titulo = titulo.strip()  # Quita espacios al inicio y al final
        if not titulo:
            raise ValueError("El título no puede estar vacío.")
        tarea = Tarea(id=self._siguiente_id(), titulo=titulo)
        self._tareas.append(tarea)
        self._guardar()
        return tarea

    def listar(self, solo_pendientes: bool = False) -> list[Tarea]:
        """HU-02: devuelve las tareas (todas o solo las pendientes)."""
        if solo_pendientes:
            return [t for t in self._tareas if not t.completada]
        return list(self._tareas)  # Copia, para no exponer la lista interna

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
