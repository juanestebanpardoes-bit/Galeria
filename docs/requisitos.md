# Requisitos del Gestor de Tareas

## Historias de usuario

| ID | Historia | Prioridad |
|---|---|---|
| HU-01 | Como usuario, quiero agregar una tarea con un título, para no olvidarla. | Alta |
| HU-02 | Como usuario, quiero ver mi lista de tareas, para saber qué tengo pendiente. | Alta |
| HU-03 | Como usuario, quiero marcar una tarea como completada, para llevar mi progreso. | Alta |
| HU-04 | Como usuario, quiero eliminar una tarea, para limpiar mi lista. | Media |
| HU-05 | Como usuario, quiero que mis tareas se guarden al cerrar el programa, para no perderlas. | Alta |

## Requisitos funcionales

- RF-01: el sistema permite crear tareas con título no vacío.
- RF-02: el sistema lista todas las tareas indicando su estado.
- RF-03: el sistema permite completar una tarea por su número (id).
- RF-04: el sistema permite eliminar una tarea por su id.
- RF-05: el sistema guarda y recupera las tareas desde un archivo JSON.

## Requisitos no funcionales

- RNF-01: debe funcionar en Python 3.10+ sin instalar dependencias.
- RNF-02: debe mostrar mensajes de error claros, sin cerrarse de forma inesperada.
- RNF-03: el código debe estar organizado en módulos y comentado.

## Criterios de aceptación (HU-01)

- Dado que el programa está abierto, cuando escribo el título "Estudiar Git", entonces la tarea aparece en la lista como pendiente.
- Dado que escribo un título vacío, entonces el sistema muestra un error y no crea la tarea.

## Versión v0.2.0: prioridades

| ID | Historia | Prioridad |
|---|---|---|
| HU-06 | Como usuario, quiero asignar una prioridad (alta, media o baja) a cada tarea y verlas ordenadas por prioridad, para atender primero lo más importante. | Media |

- RF-06: al crear una tarea el usuario puede elegir su prioridad; si no elige ninguna, es "media".
- RF-07: el sistema puede listar las tareas ordenadas de la más a la menos prioritaria.
- RF-08: las tareas guardadas con la versión v0.1.0 (sin prioridad) deben seguir funcionando.

**Criterio de aceptación:** dado que tengo una tarea "baja" y otra "alta", cuando elijo ver las tareas por prioridad, entonces la "alta" aparece primero.
