"""
main.py
-------
Punto de entrada del programa. Muestra el menú, lee lo que escribe el usuario
y llama al GestorTareas. No contiene reglas de negocio.

Ejecutar con:  python main.py   (o python3 main.py en Mac/Linux)
"""

from services import GestorTareas

MENU = """
===== GESTOR DE TAREAS =====
1. Agregar tarea
2. Ver todas las tareas
3. Ver tareas pendientes
4. Completar tarea
5. Eliminar tarea
0. Salir
"""


def mostrar_tareas(tareas) -> None:
    """Imprime una lista de tareas en formato legible."""
    if not tareas:
        print("No hay tareas para mostrar.")
        return
    for t in tareas:
        estado = "[x]" if t.completada else "[ ]"
        print(f"{t.id:>3}. {estado} {t.titulo}")


def pedir_id() -> int:
    """Pide un número al usuario. Lanza ValueError si no es un entero."""
    return int(input("Id de la tarea: "))


def main() -> None:
    """Bucle principal del programa."""
    gestor = GestorTareas()

    while True:
        print(MENU)
        opcion = input("Elige una opción: ").strip()

        # try/except: si algo falla mostramos un mensaje claro (RNF-02)
        try:
            if opcion == "1":
                tarea = gestor.agregar(input("Título: "))
                print(f"Tarea creada con id {tarea.id}.")
            elif opcion == "2":
                mostrar_tareas(gestor.listar())
            elif opcion == "3":
                mostrar_tareas(gestor.listar(solo_pendientes=True))
            elif opcion == "4":
                gestor.completar(pedir_id())
                print("Tarea completada.")
            elif opcion == "5":
                gestor.eliminar(pedir_id())
                print("Tarea eliminada.")
            elif opcion == "0":
                print("¡Hasta pronto!")
                break
            else:
                print("Opción no válida.")
        except ValueError as error:
            # Ocurre con títulos vacíos o ids que no son números
            print(f"Dato inválido: {error}")
        except LookupError as error:
            # Ocurre cuando el id no existe
            print(f"Error: {error}")


# Solo ejecuta main() si el archivo se corre directamente
# (no cuando otro archivo lo importa, como en las pruebas).
if __name__ == "__main__":
    main()
