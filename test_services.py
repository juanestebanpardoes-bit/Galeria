"""
test_services.py
----------------
Pruebas unitarias del GestorTareas con el módulo unittest de Python.
Cada método que empieza por 'test_' es una prueba independiente.
"""

import tempfile
import unittest
from datetime import datetime
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

    def test_completar_tarea_quita_recordatorio(self):
        self.gestor.agregar("A")
        self.gestor.configurar_recordatorio(1, "2099-01-01 10:00")
        self.assertIsNone(self.gestor.completar(1).recordatorio_en)

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


    # --- HU-06: prioridades (v0.2.0) ---
    def test_prioridad_por_defecto_es_media(self):
        tarea = self.gestor.agregar("A")
        self.assertEqual(tarea.prioridad, "media")

    def test_agregar_con_prioridad_valida(self):
        # Debe aceptar mayúsculas y espacios: se normalizan a "alta"
        tarea = self.gestor.agregar("A", "  ALTA ")
        self.assertEqual(tarea.prioridad, "alta")

    def test_prioridad_invalida_lanza_error(self):
        with self.assertRaises(ValueError):
            self.gestor.agregar("A", "urgentisima")

    def test_listar_por_prioridad_ordena_de_alta_a_baja(self):
        self.gestor.agregar("Baja", "baja")
        self.gestor.agregar("Alta", "alta")
        self.gestor.agregar("Media", "media")
        titulos = [t.titulo for t in self.gestor.listar(por_prioridad=True)]
        self.assertEqual(titulos, ["Alta", "Media", "Baja"])

    def test_archivo_antiguo_sin_prioridad_se_carga(self):
        # Simula un tareas.json creado con v0.1.0 (sin el campo 'prioridad')
        import json
        antiguo = [{"id": 1, "titulo": "Vieja", "completada": False,
                    "creada_en": "2026-01-01T00:00:00"}]
        self.ruta.write_text(json.dumps(antiguo), encoding="utf-8")
        gestor = GestorTareas(self.ruta)
        self.assertEqual(gestor.listar()[0].prioridad, "media")
        self.assertIsNone(gestor.listar()[0].recordatorio_en)


    # --- HU-08, HU-09 y HU-10 (v0.3.0) ---
    def test_editar_titulo_y_prioridad(self):
        self.gestor.agregar("Vieja", "baja")
        tarea = self.gestor.editar(1, titulo="  Nueva  ", prioridad="ALTA")
        self.assertEqual(tarea.titulo, "Nueva")
        self.assertEqual(tarea.prioridad, "alta")

    def test_configurar_recordatorio_persiste_en_disco(self):
        self.gestor.agregar("Estudiar")
        self.gestor.configurar_recordatorio(1, "2099-01-01 10:00")
        otra_instancia = GestorTareas(self.ruta)
        self.assertEqual(
            otra_instancia.obtener(1).recordatorio_en, "2099-01-01T10:00")

    def test_configurar_recordatorio_relativo_guarda_fecha_futura(self):
        self.gestor.agregar("Estudiar")
        tarea = self.gestor.configurar_recordatorio_relativo(1, "dia")
        fecha = datetime.fromisoformat(tarea.recordatorio_en)
        self.assertGreater(fecha, datetime.now())

    def test_configurar_recordatorio_relativo_rechaza_periodo_invalido(self):
        self.gestor.agregar("Estudiar")
        with self.assertRaises(ValueError):
            self.gestor.configurar_recordatorio_relativo(1, "año")

    def test_sumar_mes_ajusta_al_ultimo_dia(self):
        momento = datetime(2026, 1, 31, 14, 30)
        self.assertEqual(
            GestorTareas._sumar_mes(momento), datetime(2026, 2, 28, 14, 30))

    def test_configurar_recordatorio_invalido_no_modifica_tarea(self):
        self.gestor.agregar("Estudiar")
        with self.assertRaises(ValueError):
            self.gestor.configurar_recordatorio(1, "mañana")
        self.assertIsNone(self.gestor.obtener(1).recordatorio_en)

    def test_configurar_recordatorio_pasado_lanza_error(self):
        self.gestor.agregar("Estudiar")
        with self.assertRaises(ValueError):
            self.gestor.configurar_recordatorio(1, "2000-01-01 10:00")

    def test_tarea_completada_no_acepta_recordatorio(self):
        self.gestor.agregar("Estudiar")
        self.gestor.completar(1)
        with self.assertRaises(ValueError):
            self.gestor.configurar_recordatorio(1, "2099-01-01 10:00")

    def test_editar_solo_titulo_conserva_prioridad(self):
        self.gestor.agregar("A", "baja")
        self.gestor.editar(1, titulo="B")
        self.assertEqual(self.gestor.obtener(1).prioridad, "baja")

    def test_editar_titulo_vacio_lanza_error_y_no_cambia_nada(self):
        self.gestor.agregar("Original", "alta")
        with self.assertRaises(ValueError):
            self.gestor.editar(1, titulo="   ", prioridad="baja")
        tarea = self.gestor.obtener(1)
        self.assertEqual((tarea.titulo, tarea.prioridad), ("Original", "alta"))

    def test_editar_id_inexistente_lanza_error(self):
        with self.assertRaises(LookupError):
            self.gestor.editar(99, titulo="X")

    def test_editar_persiste_en_disco(self):
        self.gestor.agregar("A")
        self.gestor.editar(1, titulo="Cambiada")
        self.assertEqual(GestorTareas(self.ruta).listar()[0].titulo, "Cambiada")

    def test_buscar_por_texto_ignora_mayusculas(self):
        self.gestor.agregar("Estudiar Git")
        self.gestor.agregar("Comprar pan")
        titulos = [t.titulo for t in self.gestor.listar(texto="  gIt ")]
        self.assertEqual(titulos, ["Estudiar Git"])

    def test_listar_solo_completadas(self):
        self.gestor.agregar("A")
        self.gestor.agregar("B")
        self.gestor.completar(2)
        self.assertEqual([t.titulo for t in self.gestor.listar(solo_completadas=True)], ["B"])

    def test_estadisticas(self):
        self.gestor.agregar("A")
        self.gestor.agregar("B")
        self.gestor.completar(1)
        self.assertEqual(self.gestor.estadisticas(), (2, 1))


if __name__ == "__main__":
    unittest.main()
