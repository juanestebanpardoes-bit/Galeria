"""
services.py  (versión v0.3.0)
-----------
Contiene las REGLAS del negocio: qué se puede hacer con las tareas y qué
validaciones se aplican. No imprime ni pide datos al usuario: de eso se
encargan las interfaces (main.py en consola y gui.py en ventanas).

NOVEDADES v0.3.0:
  - obtener()      : devuelve una tarea por su id.
  - editar()       : cambia el título y/o la prioridad de una tarea.
  - listar()       : ahora también filtra por texto y por tareas completadas.
  - estadisticas() : cuenta cuántas tareas hay y cuántas están completadas.
  - _validar_titulo() y _validar_prioridad(): validaciones compartidas, para
    no repetir el mismo código en agregar() y editar().
"""

from pathlib import Path

from models import Tarea, PRIORIDADES
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

    @staticmethod
    def _validar_titulo(titulo: str) -> str:
        """NUEVO: quita espacios sobrantes y exige que el título no esté vacío."""
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("El título no puede estar vacío.")
        return titulo

    @staticmethod
    def _validar_prioridad(prioridad: str) -> str:
        """NUEVO: normaliza (minúsculas, sin espacios) y exige una prioridad válida."""
        prioridad = prioridad.strip().lower()
        if prioridad not in PRIORIDADES:
            raise ValueError("La prioridad debe ser: " + ", ".join(PRIORIDADES) + ".")
        return prioridad

    # ---------- Operaciones públicas ----------

    def agregar(self, titulo: str, prioridad: str = "media") -> Tarea:
        """Crea una tarea (HU-01 y HU-06).

        Lanza ValueError si el título está vacío o la prioridad no es válida.
        """
        titulo = self._validar_titulo(titulo)
        prioridad = self._validar_prioridad(prioridad)
        tarea = Tarea(id=self._siguiente_id(), titulo=titulo, prioridad=prioridad)
        self._tareas.append(tarea)
        self._guardar()
        return tarea

    def obtener(self, id_tarea: int) -> Tarea:
        """NUEVO: devuelve la tarea con ese id. Lanza LookupError si no existe."""
        return self._buscar(id_tarea)

    def listar(self, solo_pendientes: bool = False, por_prioridad: bool = False,
               texto: str = "", solo_completadas: bool = False) -> list[Tarea]:
        """Devuelve las tareas aplicando los filtros pedidos (HU-02, HU-06, HU-09).

        solo_pendientes:  si es True, omite las completadas.
        solo_completadas: si es True, omite las pendientes.
        texto:            si no está vacío, deja solo las tareas cuyo título
                          contiene ese texto (sin distinguir mayúsculas).
        por_prioridad:    si es True, ordena de alta a baja.
        """
        if solo_pendientes and solo_completadas:
            raise ValueError("No se puede pedir solo pendientes y solo completadas a la vez.")

        tareas = list(self._tareas)  # Copia, para no exponer la lista interna

        if solo_pendientes:
            tareas = [t for t in tareas if not t.completada]
        if solo_completadas:
            tareas = [t for t in tareas if t.completada]

        texto = texto.strip().lower()
        if texto:
            tareas = [t for t in tareas if texto in t.titulo.lower()]

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

    def editar(self, id_tarea: int, titulo: str | None = None,
               prioridad: str | None = None) -> Tarea:
        """NUEVO (HU-08): cambia el título y/o la prioridad de una tarea.

        Los datos que no se envían (None) se dejan como estaban. Se valida
        TODO antes de modificar la tarea: si algo es inválido, no cambia nada.
        """
        tarea = self._buscar(id_tarea)
        nuevo_titulo = tarea.titulo if titulo is None else self._validar_titulo(titulo)
        nueva_prioridad = (tarea.prioridad if prioridad is None
                           else self._validar_prioridad(prioridad))
        tarea.titulo = nuevo_titulo
        tarea.prioridad = nueva_prioridad
        self._guardar()
        return tarea

    def eliminar(self, id_tarea: int) -> None:
        """HU-04: elimina una tarea por su id."""
        tarea = self._buscar(id_tarea)
        self._tareas.remove(tarea)
        self._guardar()

    def estadisticas(self) -> tuple[int, int]:
        """NUEVO (HU-10): devuelve (total de tareas, tareas completadas)."""
        completadas = sum(1 for t in self._tareas if t.completada)
        return len(self._tareas), completadas
