"""
test_services.py
----------------
Pruebas unitarias del GestorTareas con el módulo unittest de Python.
Cada método que empieza por 'test_' es una prueba independiente.
"""

import tempfile
import unittest
from pathlib import Path

from services import GestorTareas


class TestGestorTareas(unittest.TestCase):

    def setUp(self):
        """Se ejecuta ANTES de cada prueba: crea un archivo temporal limpio,
        así las pruebas no tocan el tareas.json real del usuario."""
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = Path(self.carpeta.name) / "tareas.json"
        self.gestor = GestorTareas(self.ruta)

    def tearDown(self):
        """Se ejecuta DESPUÉS de cada prueba: borra los archivos temporales."""
        self.carpeta.cleanup()

    # --- HU-01: agregar ---
    def test_agregar_tarea_valida(self):
        tarea = self.gestor.agregar("Estudiar Git")
        self.assertEqual(tarea.id, 1)
        self.assertEqual(tarea.titulo, "Estudiar Git")
        self.assertFalse(tarea.completada)

    def test_agregar_titulo_vacio_lanza_error(self):
        with self.assertRaises(ValueError):
            self.gestor.agregar("   ")

    def test_ids_son_consecutivos(self):
        self.gestor.agregar("A")
        segunda = self.gestor.agregar("B")
        self.assertEqual(segunda.id, 2)

    # --- HU-02: listar ---
    def test_listar_solo_pendientes(self):
        self.gestor.agregar("A")
        self.gestor.agregar("B")
        self.gestor.completar(1)
        pendientes = self.gestor.listar(solo_pendientes=True)
        self.assertEqual([t.titulo for t in pendientes], ["B"])

    # --- HU-03: completar ---
    def test_completar_tarea(self):
        self.gestor.agregar("A")
        self.assertTrue(self.gestor.completar(1).completada)

    def test_completar_id_inexistente_lanza_error(self):
        with self.assertRaises(LookupError):
            self.gestor.completar(99)

    # --- HU-04: eliminar ---
    def test_eliminar_tarea(self):
        self.gestor.agregar("A")
        self.gestor.eliminar(1)
        self.assertEqual(self.gestor.listar(), [])

    # --- HU-05: persistencia ---
    def test_las_tareas_persisten_en_disco(self):
        self.gestor.agregar("Persistente")
        # Creamos OTRO gestor que lee el mismo archivo
        otro = GestorTareas(self.ruta)
        self.assertEqual(otro.listar()[0].titulo, "Persistente")


if __name__ == "__main__":
    unittest.main()
