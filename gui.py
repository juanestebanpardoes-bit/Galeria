"""
gui.py  (versión v0.3.0)
------
Interfaz GRÁFICA del Gestor de Tareas, hecha con tkinter (viene incluido con
Python, no hay que instalar nada).

Idea clave de la arquitectura en capas: este archivo SOLO se ocupa de dibujar
ventanas y de reaccionar a los clics. Todas las reglas (validar títulos,
guardar en el JSON, ordenar...) siguen estando en services.py. Por eso main.py
(la versión de consola) y gui.py (la versión con ventanas) funcionan con el
MISMO gestor y el MISMO archivo tareas.json.

Ejecutar con:  python gui.py   (o python3 gui.py en Mac/Linux)

Conceptos de tkinter que se usan aquí:
  - Ventana raíz (tk.Tk):    la ventana principal del programa.
  - Widget:                  cualquier elemento visible (botón, etiqueta, tabla...).
  - Gestor de disposición:   pack() / grid() colocan los widgets dentro de la ventana.
  - Variable de control:     StringVar, BooleanVar, DoubleVar. Se enlazan a un widget
                             y cuando cambia la variable, cambia lo que se ve (y viceversa).
  - Evento / command:        función que se ejecuta cuando el usuario hace algo
                             (clic, tecla Enter, doble clic...).
  - mainloop():              bucle que mantiene la ventana abierta esperando eventos.
"""

from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox  # ttk = widgets con aspecto moderno

from models import PRIORIDADES
from services import GestorTareas

# =============================================================================
# 1. CONSTANTES DE DISEÑO (colores y fuente)
# Se definen en un solo lugar: para cambiar el aspecto del programa basta con
# modificar estos valores. Los colores se escriben en formato hexadecimal #RRGGBB.
# =============================================================================
COLOR_FONDO = "#FFFFFF"            # blanco (fondo general)
COLOR_PRIMARIO = "#87CEEB"         # azul celeste (encabezado y botones)
COLOR_PRIMARIO_OSCURO = "#6CBFE3"  # azul celeste más oscuro al pasar el mouse
COLOR_TEXTO = "#000000"            # negro
COLOR_EXITO = "#2E7D32"            # verde (botón Completar, barra de progreso)
COLOR_PELIGRO = "#C62828"          # rojo (botón Eliminar)
COLOR_TEXTO_APAGADO = "#000000"    # negro (tareas ya completadas)
COLOR_RECORDATORIO_VENCIDO = "#FF8A80"  # rojo suave para recordatorios vencidos

# Color de fondo de cada fila de la tabla según la prioridad de la tarea
COLORES_PRIORIDAD = {
    "alta": "#FFCDD2",   # rojo suave
    "media": "#FFF9C4",  # amarillo suave
    "baja": "#C8E6C9",   # verde suave
}

FUENTE = ("Comic Sans MS", 10)


# =============================================================================
# 2. VENTANA SECUNDARIA: EDITAR UNA TAREA
# Una ventana "hija" (tk.Toplevel) que aparece encima de la principal.
# =============================================================================
class VentanaEditar(tk.Toplevel):
    """Ventana emergente para cambiar el título y la prioridad de una tarea.

    No sabe nada de servicios ni de archivos: cuando el usuario pulsa Guardar
    llama a la función `al_guardar` que le entregó la ventana principal.
    """

    def __init__(self, padre, tarea, al_guardar):
        """
        padre:      ventana sobre la que aparece (la principal).
        tarea:      la Tarea que se va a editar (para mostrar sus valores actuales).
        al_guardar: función que recibe (titulo, prioridad) y hace el cambio real.
        """
        super().__init__(padre)  # crea la ventana Toplevel
        self._al_guardar = al_guardar

        self.title(f"Editar tarea #{tarea.id}")
        self.configure(bg=COLOR_FONDO, padx=20, pady=16)
        self.resizable(False, False)  # tamaño fijo
        self.transient(padre)         # se mantiene delante de la ventana principal
        self.wait_visibility()        # espera a que la ventana sea visible (evita errores en Linux)
        self.grab_set()               # MODAL: bloquea la ventana principal hasta cerrar esta

        # Variables enlazadas a los campos: empiezan con los valores actuales
        self.var_titulo = tk.StringVar(value=tarea.titulo)
        self.var_prioridad = tk.StringVar(value=tarea.prioridad)

        # --- Campos del formulario, colocados con grid() (filas y columnas) ---
        ttk.Label(self, text="Título:").grid(row=0, column=0, sticky="w")
        self.entrada = ttk.Entry(self, textvariable=self.var_titulo, width=45)
        self.entrada.grid(row=1, column=0, columnspan=2, pady=(2, 12))

        ttk.Label(self, text="Prioridad:").grid(row=2, column=0, sticky="w")
        # Combobox "readonly": lista desplegable donde solo se puede elegir
        ttk.Combobox(self, textvariable=self.var_prioridad, values=PRIORIDADES,
                     state="readonly", width=12).grid(row=3, column=0, sticky="w")

        botones = ttk.Frame(self)
        botones.grid(row=3, column=1, sticky="e")
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Guardar", style="Accion.TButton",
                   command=self._guardar).pack(side="left")

        # Atajos de teclado: Enter guarda, Escape cancela
        self.bind("<Return>", lambda _evento: self._guardar())
        self.bind("<Escape>", lambda _evento: self.destroy())

        self.entrada.focus_set()           # el cursor empieza en el campo de título
        self.entrada.select_range(0, "end")  # y el texto queda seleccionado
        self._centrar_sobre(padre)

    def _centrar_sobre(self, padre):
        """Coloca esta ventana en el centro de la ventana principal."""
        self.update_idletasks()  # fuerza a tkinter a calcular el tamaño real
        x = padre.winfo_rootx() + (padre.winfo_width() - self.winfo_width()) // 2
        y = padre.winfo_rooty() + (padre.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")  # "+x+y" = posición en pantalla

    def _guardar(self):
        """Pide a la ventana principal que guarde; si hay error, lo muestra."""
        try:
            self._al_guardar(self.var_titulo.get(), self.var_prioridad.get())
        except (ValueError, LookupError) as error:
            # Los errores de las reglas de negocio llegan como excepciones:
            # aquí los convertimos en una ventanita de aviso y NO cerramos.
            messagebox.showwarning("No se pudo guardar", str(error), parent=self)
            return
        self.destroy()  # todo salió bien: se cierra la ventana


class VentanaRecordatorio(tk.Toplevel):
    """Ventana para programar o quitar el recordatorio de una tarea."""

    def __init__(self, padre, tarea, al_guardar):
        super().__init__(padre)
        self._al_guardar = al_guardar

        self.title(f"Recordatorio para la tarea #{tarea.id}")
        self.configure(bg=COLOR_FONDO, padx=20, pady=16)
        self.resizable(False, False)
        self.transient(padre)
        self.wait_visibility()
        self.grab_set()

        if tarea.recordatorio_en:
            ttk.Label(
                self, text=f"Recordatorio actual: {tarea.recordatorio_en.replace('T', ' ')}"
            ).pack(anchor="w", pady=(0, 10))
        ttk.Label(self, text="¿Cuándo quieres que te lo recuerde?").pack(
            anchor="w", pady=(0, 6))
        for texto, periodo in (
            ("Al día siguiente", "dia"),
            ("A la semana siguiente", "semana"),
            ("Al mes siguiente", "mes"),
        ):
            ttk.Button(
                self, text=texto, style="Accion.TButton",
                command=lambda p=periodo: self._programar(p)
            ).pack(fill="x", pady=3)

        botones = ttk.Frame(self)
        botones.pack(anchor="e", pady=(10, 0))
        if tarea.recordatorio_en:
            ttk.Button(botones, text="Quitar", command=self._quitar).pack(
                side="left", padx=(0, 6))
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(
            side="left")

        self.bind("<Escape>", lambda _evento: self.destroy())
        self._centrar_sobre(padre)

    def _programar(self, periodo):
        try:
            self._al_guardar(periodo)
        except (ValueError, LookupError) as error:
            messagebox.showwarning("No se pudo guardar", str(error), parent=self)
            return
        self.destroy()

    def _centrar_sobre(self, padre):
        self.update_idletasks()
        x = padre.winfo_rootx() + (padre.winfo_width() - self.winfo_width()) // 2
        y = padre.winfo_rooty() + (padre.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _quitar(self):
        try:
            self._al_guardar(None)
        except (ValueError, LookupError) as error:
            messagebox.showwarning("No se pudo quitar", str(error), parent=self)
            return
        self.destroy()


# =============================================================================
# 3. VENTANA PRINCIPAL
# =============================================================================
class AplicacionTareas:
    """Construye y controla la ventana principal del gestor de tareas."""

    def __init__(self, raiz: tk.Tk, gestor: GestorTareas):
        """
        raiz:   la ventana principal de tkinter (tk.Tk()).
        gestor: el GestorTareas de services.py, que contiene las reglas de negocio.
        """
        self.raiz = raiz
        self.gestor = gestor
        self._recordatorios_notificados: set[tuple[int, str]] = set()
        self.raiz.option_add("*Font", FUENTE)

        # Variables de control: guardan lo que el usuario escribe o elige
        self.var_titulo = tk.StringVar()                 # texto de la nueva tarea
        self.var_prioridad = tk.StringVar(value="media")  # prioridad de la nueva tarea
        self.var_filtro = tk.StringVar(value="todas")    # todas / pendientes / completadas
        self.var_busqueda = tk.StringVar()               # texto del buscador
        self.var_ordenar = tk.BooleanVar(value=False)    # ¿ordenar por prioridad?
        self.var_progreso = tk.DoubleVar(value=0)        # 0 a 100 (barra de progreso)
        self.var_resumen = tk.StringVar()                # "3 de 5 tareas completadas"
        self.var_estado = tk.StringVar(value="Listo.")   # mensaje de la barra inferior

        # Se construye la pantalla por partes, de arriba hacia abajo
        self._configurar_ventana()
        self._configurar_estilos()
        self._crear_menu()
        self._crear_encabezado()
        self._crear_barra_estado()   # se crea antes del cuerpo para que quede abajo
        self._crear_cuerpo()

        self.refrescar()  # llena la tabla con las tareas guardadas
        self.raiz.after(1000, self._revisar_recordatorios)

    # ------------------------------------------------------------------
    # 3.1 Configuración general de la ventana
    # ------------------------------------------------------------------
    def _configurar_ventana(self):
        """Título, tamaño y posición de la ventana principal."""
        self.raiz.title("Programa Juan Centralo")
        self.raiz.configure(bg=COLOR_FONDO)
        ancho, alto = 860, 640
        # Calcula la esquina superior izquierda para que la ventana quede centrada
        x = (self.raiz.winfo_screenwidth() - ancho) // 2
        y = (self.raiz.winfo_screenheight() - alto) // 2
        self.raiz.geometry(f"{ancho}x{alto}+{x}+{y}")  # formato: ANCHOxALTO+X+Y
        self.raiz.minsize(720, 520)  # tamaño mínimo al redimensionar

    def _configurar_estilos(self):
        """Define el aspecto (colores, fuentes, márgenes) de los widgets ttk."""
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")  # tema que permite cambiar colores en todos los sistemas

        # "." significa "todos los widgets"
        estilo.configure(".", font=FUENTE, background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TButton", font=FUENTE, padding=(12, 6))

        # Estilos propios: se usan con style="Nombre.TButton" al crear el botón
        for nombre, color, color_hover in (
            ("Accion", COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO),
            ("Exito", "#81C784", "#66BB6A"),
            ("Peligro", "#EF9A9A", "#E57373"),
            ("Editar", "#FFEB3B", "#FDD835"),
            ("Recordatorio", "#FFEB3B", "#FDD835"),
        ):
            estilo.configure(f"{nombre}.TButton", background=color, foreground=COLOR_TEXTO)
            # map(): cambia el aspecto según el estado; "active" = mouse encima
            estilo.map(f"{nombre}.TButton", background=[("active", color_hover)],
                       foreground=[("disabled", COLOR_TEXTO)])

        # Tabla: filas más altas y encabezado de color
        estilo.configure("Treeview", rowheight=30, background="#FFFFFF",
                         fieldbackground="#FFFFFF", foreground=COLOR_TEXTO)
        estilo.configure("Treeview.Heading", font=(FUENTE[0], 10, "bold"),
                         background=COLOR_PRIMARIO, foreground=COLOR_TEXTO, padding=6)
        estilo.map("Treeview.Heading", background=[("active", COLOR_PRIMARIO_OSCURO)])

        # Barra de progreso verde
        estilo.configure("Verde.Horizontal.TProgressbar", troughcolor="#DDE1EE",
                         background=COLOR_EXITO, thickness=18)

        # Recuadros con título y barra de estado
        estilo.configure("TLabelframe", background=COLOR_FONDO)
        estilo.configure("TLabelframe.Label", background=COLOR_FONDO,
                         foreground=COLOR_TEXTO, font=(FUENTE[0], 10, "bold"))
        estilo.configure("Estado.TLabel", background="#FFFFFF", foreground=COLOR_TEXTO,
                         padding=(10, 5))

    # ------------------------------------------------------------------
    # 3.2 Menú superior (Archivo / Ayuda)
    # ------------------------------------------------------------------
    def _crear_menu(self):
        """Crea la barra de menú de la parte superior de la ventana."""
        barra = tk.Menu(self.raiz, bg=COLOR_FONDO, fg=COLOR_TEXTO,
                        activebackground=COLOR_PRIMARIO_OSCURO, activeforeground=COLOR_TEXTO)

        menu_archivo = tk.Menu(
            barra, tearoff=False, bg=COLOR_FONDO, fg=COLOR_TEXTO,
            activebackground=COLOR_PRIMARIO_OSCURO, activeforeground=COLOR_TEXTO)
        menu_archivo.add_command(label="Salir", command=self.raiz.destroy)
        barra.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ayuda = tk.Menu(
            barra, tearoff=False, bg=COLOR_FONDO, fg=COLOR_TEXTO,
            activebackground=COLOR_PRIMARIO_OSCURO, activeforeground=COLOR_TEXTO)
        menu_ayuda.add_command(label="Acerca de...", command=self.acerca_de)
        barra.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.raiz.config(menu=barra)

    # ------------------------------------------------------------------
    # 3.3 Encabezado de color
    # ------------------------------------------------------------------
    def _crear_encabezado(self):
        """Franja azul superior con el nombre de la aplicación."""
        # Aquí se usa tk.Frame/tk.Label (no ttk) porque aceptan bg= directamente
        encabezado = tk.Frame(self.raiz, bg=COLOR_PRIMARIO)
        encabezado.pack(side="top", fill="x")  # fill="x": ocupa todo el ancho

        tk.Label(encabezado, text="✔  Programa Juan", bg=COLOR_PRIMARIO, fg=COLOR_TEXTO,
                 font=(FUENTE[0], 20, "bold")).pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(encabezado, text="Organiza tu día: agrega, prioriza, edita y completa tus tareas",
                 bg=COLOR_PRIMARIO, fg=COLOR_TEXTO,
                 font=(FUENTE[0], 10)).pack(anchor="w", padx=22, pady=(0, 14))

    # ------------------------------------------------------------------
    # 3.4 Barra de estado inferior
    # ------------------------------------------------------------------
    def _crear_barra_estado(self):
        """Línea inferior que muestra mensajes como 'Tarea agregada'."""
        ttk.Label(self.raiz, textvariable=self.var_estado,
                  style="Estado.TLabel").pack(side="bottom", fill="x")

    # ------------------------------------------------------------------
    # 3.5 Cuerpo: formulario, filtros, tabla, botones y progreso
    # ------------------------------------------------------------------
    def _crear_cuerpo(self):
        """Zona central de la ventana."""
        cuerpo = ttk.Frame(self.raiz, padding=16)
        cuerpo.pack(side="top", fill="both", expand=True)  # expand: usa el espacio sobrante

        self._crear_formulario(cuerpo)
        self._crear_filtros(cuerpo)
        self._crear_tabla(cuerpo)
        self._crear_botones(cuerpo)
        self._crear_progreso(cuerpo)

    def _crear_formulario(self, padre):
        """Fila para escribir una tarea nueva y elegir su prioridad."""
        marco = ttk.LabelFrame(padre, text=" Nueva tarea ", padding=10)
        marco.pack(fill="x")

        ttk.Label(marco, text="Título:").pack(side="left")
        self.entrada_titulo = ttk.Entry(marco, textvariable=self.var_titulo)
        self.entrada_titulo.pack(side="left", fill="x", expand=True, padx=8)
        # Pulsar Enter dentro de la caja equivale a pulsar el botón Agregar
        self.entrada_titulo.bind("<Return>", lambda _evento: self.agregar())

        ttk.Label(marco, text="Prioridad:").pack(side="left")
        ttk.Combobox(marco, textvariable=self.var_prioridad, values=PRIORIDADES,
                     state="readonly", width=8).pack(side="left", padx=8)

        ttk.Button(marco, text="Agregar", style="Accion.TButton",
                   command=self.agregar).pack(side="left")
        self.entrada_titulo.focus_set()  # el cursor empieza en esta caja

    def _crear_filtros(self, padre):
        """Opciones para filtrar, buscar y ordenar lo que se ve en la tabla."""
        marco = ttk.LabelFrame(padre, text=" Ver y buscar ", padding=10)
        marco.pack(fill="x", pady=(10, 0))

        # Tres botones de opción: solo se puede elegir uno, todos comparten var_filtro
        for texto, valor in (("Todas", "todas"), ("Pendientes", "pendientes"),
                             ("Completadas", "completadas")):
            ttk.Radiobutton(marco, text=texto, value=valor, variable=self.var_filtro,
                            command=self.refrescar).pack(side="left", padx=(0, 10))

        ttk.Checkbutton(marco, text="Ordenar por prioridad", variable=self.var_ordenar,
                        command=self.refrescar).pack(side="left", padx=(10, 10))

        ttk.Label(marco, text="Buscar:").pack(side="left", padx=(10, 4))
        ttk.Entry(marco, textvariable=self.var_busqueda, width=20).pack(side="left")
        # trace_add("write", ...): ejecuta la función cada vez que cambia el texto,
        # así la tabla se filtra mientras escribes, sin pulsar ningún botón.
        self.var_busqueda.trace_add("write", lambda *_args: self.refrescar())

    def _crear_tabla(self, padre):
        """Tabla (Treeview) con la lista de tareas y su barra de desplazamiento."""
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True, pady=10)

        # (identificador de columna, título visible, ancho en píxeles, alineación)
        columnas = (
            ("id", "#", 50, "center"),
            ("estado", "Estado", 110, "center"),
            ("prioridad", "Prioridad", 90, "center"),
            ("titulo", "Tarea", 270, "w"),
            ("creada", "Creada", 130, "center"),
            ("recordatorio", "Recordatorio", 145, "center"),
        )
        self.tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas],
                                  show="headings",       # sin la columna extra de árbol
                                  selectmode="browse")   # se selecciona una fila a la vez
        for identificador, texto, ancho, ancla in columnas:
            self.tabla.heading(identificador, text=texto)
            # stretch=True: solo la columna "titulo" crece cuando se agranda la ventana
            self.tabla.column(identificador, width=ancho, anchor=ancla,
                              stretch=(identificador == "titulo"))

        # "Tags" (etiquetas de fila): permiten dar color según la prioridad
        for prioridad, color in COLORES_PRIORIDAD.items():
            self.tabla.tag_configure(prioridad, background=color)
        self.tabla.tag_configure(
            "recordatorio_vencido", background=COLOR_RECORDATORIO_VENCIDO)
        self.tabla.tag_configure("hecha", foreground=COLOR_TEXTO_APAGADO)

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)  # conecta tabla y barra
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # Eventos de la tabla
        self.tabla.bind("<Double-1>", self._al_doble_clic)       # doble clic = editar
        self.tabla.bind("<Delete>", lambda _evento: self.eliminar())  # tecla Supr

    def _crear_botones(self, padre):
        """Botones de acción sobre la tarea seleccionada."""
        marco = ttk.Frame(padre)
        marco.pack(fill="x")
        ttk.Button(marco, text="Completar", style="Exito.TButton",
                   command=self.completar).pack(side="left")
        ttk.Button(marco, text="Editar", style="Editar.TButton",
                   command=self.editar).pack(side="left", padx=8)
        ttk.Button(marco, text="Recordatorio", style="Recordatorio.TButton",
                   command=self.configurar_recordatorio).pack(side="left", padx=8)
        ttk.Button(marco, text="Eliminar", style="Peligro.TButton",
                   command=self.eliminar).pack(side="left")

    def _crear_progreso(self, padre):
        """Barra que muestra qué porcentaje de las tareas está completado."""
        marco = ttk.LabelFrame(padre, text=" Progreso ", padding=10)
        marco.pack(fill="x", pady=(12, 0))
        ttk.Progressbar(marco, variable=self.var_progreso, maximum=100,
                        style="Verde.Horizontal.TProgressbar").pack(fill="x")
        ttk.Label(marco, textvariable=self.var_resumen).pack(anchor="w", pady=(6, 0))

    # ------------------------------------------------------------------
    # 3.6 Acciones: se ejecutan cuando el usuario pulsa un botón o una tecla
    # Patrón de todas: 1) pedir algo al gestor  2) si falla, avisar con una
    # ventanita  3) si sale bien, refrescar la tabla y escribir un mensaje.
    # ------------------------------------------------------------------
    def agregar(self):
        """Botón Agregar / tecla Enter: crea una tarea con el título escrito."""
        try:
            tarea = self.gestor.agregar(self.var_titulo.get(), self.var_prioridad.get())
        except ValueError as error:  # por ejemplo, título vacío
            messagebox.showwarning("Dato inválido", str(error))
            return
        self.var_titulo.set("")           # limpia la caja de texto
        self.entrada_titulo.focus_set()   # devuelve el cursor para escribir otra tarea
        self.refrescar()
        self.var_estado.set(f"Tarea {tarea.id} agregada.")

    def completar(self):
        """Botón Completar: marca como hecha la tarea seleccionada."""
        id_tarea = self._pedir_seleccion()
        if id_tarea is None:
            return
        try:
            self.gestor.completar(id_tarea)
        except LookupError as error:
            messagebox.showerror("Error", str(error))
            return
        self.refrescar()
        self.var_estado.set(f"Tarea {id_tarea} completada.")

    def editar(self):
        """Botón Editar / doble clic: abre la ventana de edición."""
        id_tarea = self._pedir_seleccion()
        if id_tarea is None:
            return
        tarea = self.gestor.obtener(id_tarea)

        def guardar(titulo, prioridad):
            """Función que la ventana de edición llamará al pulsar Guardar.
            Si el gestor lanza un error, se propaga a VentanaEditar, que lo muestra."""
            self.gestor.editar(id_tarea, titulo=titulo, prioridad=prioridad)
            self.refrescar()
            self.var_estado.set(f"Tarea {id_tarea} actualizada.")

        VentanaEditar(self.raiz, tarea, guardar)

    def configurar_recordatorio(self):
        """Abre el formulario para programar o quitar un recordatorio."""
        id_tarea = self._pedir_seleccion()
        if id_tarea is None:
            return
        tarea = self.gestor.obtener(id_tarea)
        if tarea.completada:
            messagebox.showinfo(
                "Tarea completada",
                "No se puede configurar un recordatorio para una tarea completada.")
            return

        def guardar(periodo):
            self.gestor.configurar_recordatorio_relativo(id_tarea, periodo)
            self.refrescar()
            self.var_estado.set(f"Recordatorio de la tarea {id_tarea} actualizado.")

        VentanaRecordatorio(self.raiz, tarea, guardar)

    def eliminar(self):
        """Botón Eliminar / tecla Supr: borra la tarea seleccionada, con confirmación."""
        id_tarea = self._pedir_seleccion()
        if id_tarea is None:
            return
        tarea = self.gestor.obtener(id_tarea)
        # askyesno devuelve True si el usuario pulsa "Sí" y False si pulsa "No"
        if not messagebox.askyesno(
                "Eliminar tarea",
                f"¿Seguro que quieres eliminar la tarea {id_tarea}?\n\n«{tarea.titulo}»\n\n"
                "Esta acción no se puede deshacer."):
            return
        self.gestor.eliminar(id_tarea)
        self.refrescar()
        self.var_estado.set(f"Tarea {id_tarea} eliminada.")

    def acerca_de(self):
        """Menú Ayuda > Acerca de: ventana informativa."""
        messagebox.showinfo(
            "Acerca de",
            "Gestor de Tareas v0.3.0\n\nProyecto del curso Fundamentos de "
            "Construcción de Software.\nHecho con Python y tkinter.")

    # ------------------------------------------------------------------
    # 3.7 Utilidades internas
    # ------------------------------------------------------------------
    def _id_seleccionado(self):
        """Devuelve el id de la fila seleccionada, o None si no hay ninguna."""
        seleccion = self.tabla.selection()  # tupla con los iid de las filas elegidas
        return int(seleccion[0]) if seleccion else None

    def _pedir_seleccion(self):
        """Como _id_seleccionado, pero avisa al usuario si no eligió ninguna tarea."""
        id_tarea = self._id_seleccionado()
        if id_tarea is None:
            messagebox.showinfo("Selecciona una tarea",
                                "Primero haz clic sobre una tarea de la lista.")
        return id_tarea

    def _al_doble_clic(self, evento):
        """Edita la tarea solo si el doble clic fue sobre una fila (no sobre el encabezado)."""
        if self.tabla.identify_region(evento.x, evento.y) == "cell":
            self.editar()

    def _revisar_recordatorios(self):
        """Muestra una vez cada recordatorio vencido y continúa revisando."""
        ahora = datetime.now()
        vencidos = [
            tarea for tarea in self.gestor.listar(solo_pendientes=True)
            if tarea.recordatorio_en
            and datetime.fromisoformat(tarea.recordatorio_en) <= ahora
            and (tarea.id, tarea.recordatorio_en) not in self._recordatorios_notificados
        ]

        if vencidos:
            self._recordatorios_notificados.update(
                (tarea.id, tarea.recordatorio_en) for tarea in vencidos)
            self.refrescar()
            for tarea in vencidos:
                messagebox.showinfo(
                    "Recordatorio de tarea",
                    f"Es hora de cumplir esta tarea:\n\n{tarea.titulo}",
                    parent=self.raiz)

        self.raiz.after(30000, self._revisar_recordatorios)

    def refrescar(self):
        """Vuelve a dibujar la tabla y la barra de progreso con los datos actuales.

        Se llama cada vez que algo cambia: al agregar, completar, editar,
        eliminar, cambiar un filtro o escribir en el buscador.
        """
        previa = self._id_seleccionado()  # para volver a seleccionarla después

        # 1) Vaciar la tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        # 2) Pedir al gestor las tareas que cumplen los filtros elegidos
        filtro = self.var_filtro.get()
        tareas = self.gestor.listar(
            solo_pendientes=(filtro == "pendientes"),
            solo_completadas=(filtro == "completadas"),
            por_prioridad=self.var_ordenar.get(),
            texto=self.var_busqueda.get(),
        )

        # 3) Insertar una fila por tarea. iid = identificador de la fila = id de la tarea
        ahora = datetime.now()
        for t in tareas:
            estado = "✔ Hecha" if t.completada else "Pendiente"
            recordatorio_vencido = (
                t.recordatorio_en
                and datetime.fromisoformat(t.recordatorio_en) <= ahora
            )
            etiqueta = (
                "hecha" if t.completada
                else "recordatorio_vencido" if recordatorio_vencido
                else t.prioridad
            )
            self.tabla.insert("", "end", iid=str(t.id), tags=(etiqueta,), values=(
                t.id, estado, t.prioridad.capitalize(), t.titulo,
                t.creada_en.replace("T", " "),
                t.recordatorio_en.replace("T", " ") if t.recordatorio_en else ""))

        # 4) Recuperar la selección anterior si esa tarea sigue visible
        if previa is not None and self.tabla.exists(str(previa)):
            self.tabla.selection_set(str(previa))

        # 5) Actualizar la barra de progreso (siempre cuenta TODAS las tareas)
        total, hechas = self.gestor.estadisticas()
        porcentaje = (hechas / total * 100) if total else 0
        self.var_progreso.set(porcentaje)
        self.var_resumen.set(f"{hechas} de {total} tareas completadas ({porcentaje:.0f}%)")


# =============================================================================
# 4. PUNTO DE ENTRADA
# =============================================================================
def main() -> None:
    """Crea la ventana, la conecta con el gestor y arranca el bucle de eventos."""
    raiz = tk.Tk()                     # 1) la ventana principal
    gestor = GestorTareas()            # 2) las reglas de negocio (lee tareas.json)
    AplicacionTareas(raiz, gestor)     # 3) dibuja la interfaz sobre esa ventana
    raiz.mainloop()                    # 4) mantiene la ventana abierta hasta cerrarla


# Solo se ejecuta main() si corres este archivo directamente (python gui.py)
if __name__ == "__main__":
    main()
