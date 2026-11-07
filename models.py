"""
models.py
---------
Define las estructuras de datos del programa.
Aquí solo hay datos: no hay menús ni lectura de archivos.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Tarea:
    """Representa una tarea del usuario.

    @dataclass genera automáticamente __init__, __repr__ y __eq__,
    así evitamos escribir código repetitivo.
    """

    id: int                      # Identificador único (1, 2, 3...)
    titulo: str                  # Texto de la tarea
    completada: bool = False     # False = pendiente, True = hecha
    # default_factory ejecuta la función cada vez que se crea una tarea,
    # así cada una guarda su propia fecha de creación.
    creada_en: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def a_diccionario(self) -> dict:
        """Convierte la tarea en un diccionario (necesario para guardarla en JSON)."""
        return asdict(self)

    @staticmethod
    def desde_diccionario(datos: dict) -> "Tarea":
        """Crea una Tarea a partir de un diccionario leído del JSON."""
        return Tarea(**datos)
