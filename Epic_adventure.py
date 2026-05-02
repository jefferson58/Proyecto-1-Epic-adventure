import tkinter as tk
from tkinter import messagebox
import random
import copy

# ==============================================================
# SECCIÓN 0 — DATOS: 15 PERSONAJES Y CONSTANTES
# ==============================================================

PERSONAJES = [
    {"nombre": "HERCULES",  "hp_max": 100, "hp": 100, "atk": 25, "def": 10, "img": "imagenes/hercules.png"},
    {"nombre": "SULLEY",    "hp_max": 140, "hp": 140, "atk": 12, "def": 20, "img": "imagenes/sulley.png"},
    {"nombre": "MULAN",     "hp_max": 110, "hp": 110, "atk": 18, "def": 15, "img": "imagenes/mulan.png"},
    {"nombre": "BUZZ",      "hp_max": 95,  "hp": 95,  "atk": 22, "def": 12, "img": "imagenes/buzz.png"},
    {"nombre": "BAYMAX",    "hp_max": 160, "hp": 160, "atk": 8,  "def": 25, "img": "imagenes/baymax.png"},
    {"nombre": "SIMBA",     "hp_max": 120, "hp": 120, "atk": 20, "def": 14, "img": "imagenes/simba.png"},
    {"nombre": "MOANA",     "hp_max": 105, "hp": 105, "atk": 19, "def": 16, "img": "imagenes/moana.png"},
    {"nombre": "STITCH",    "hp_max": 130, "hp": 130, "atk": 17, "def": 18, "img": "imagenes/stitch.png"},
    {"nombre": "ELSA",      "hp_max": 90,  "hp": 90,  "atk": 28, "def": 8,  "img": "imagenes/elsa.png"},
    {"nombre": "JACK",      "hp_max": 85,  "hp": 85,  "atk": 30, "def": 6,  "img": "imagenes/jack.png"},
    {"nombre": "TIANA",     "hp_max": 115, "hp": 115, "atk": 16, "def": 17, "img": "imagenes/tiana.png"},
    {"nombre": "RAPUNZEL",  "hp_max": 100, "hp": 100, "atk": 21, "def": 13, "img": "imagenes/rapunzel.png"},
    {"nombre": "MAUI",      "hp_max": 150, "hp": 150, "atk": 14, "def": 22, "img": "imagenes/maui.png"},
    {"nombre": "MIRABEL",   "hp_max": 108, "hp": 108, "atk": 17, "def": 16, "img": "imagenes/mirabel.png"},
    {"nombre": "RAYA",      "hp_max": 95,  "hp": 95,  "atk": 24, "def": 11, "img": "imagenes/raya.png"},
]

UBICACIONES  = ["Radiator Springs", "Pride Rock", "Monstropolis", "Arendelle", "Corona"]


def cargar_imagen(ruta, tamaño=80):
    """
    Intenta cargar una imagen PNG con tk.PhotoImage.
    Usa subsample para reducir el tamaño al valor indicado en píxeles.
    Si el archivo no existe o falla, retorna None sin romper el juego.
    tk.PhotoImage soporta PNG nativamente, no requiere librerías extra.
    """
    try:
        img = tk.PhotoImage(file=ruta)
        # Calcular cuánto reducir: dividir el ancho real entre el tamaño deseado
        factor = max(1, img.width() // tamaño)
        if factor > 1:
            img = img.subsample(factor, factor)
        return img
    except Exception:
        return None

# ==============================================================
# SECCIÓN 0b — VARIABLES GLOBALES (estado del juego)
# ==============================================================

ventana                    = None
nombre_jugador             = ""
equipo_jugador             = []
equipo_hollow              = []
puntaje_jugador            = 0
puntaje_hollow             = 0
huecos_derrotados          = 0
personaje_activo_jugador   = None
personaje_activo_hollow    = None
turno_en_progreso          = False

# Referencias a labels que se actualizan durante la batalla
lbl_hp_jugador             = None
lbl_hp_hollow              = None
lbl_puntaje                = None
lbl_nombre_pj              = None
lbl_nombre_hollow          = None
lbl_stats_jugador          = None
lbl_stats_hollow           = None
btn_atacar                 = None

# Referencias para imágenes en batalla
lbl_img_jugador            = None
lbl_img_hollow             = None
img_jugador_tk             = None
img_hollow_tk              = None

# ==============================================================
# SECCIÓN 1 — FUNCIONES DE PERSONAJES
# ==============================================================

def copiar_personaje(p):
    """Devuelve una copia del personaje para no afectar al diccionario."""
    return copy.copy(p)


def restaurar_vida(p):
    """Restaura el HP del personaje a su valor máximo."""
    p["hp"] = p["hp_max"]


def esta_vivo(p):
    """Retorna True si el personaje tiene HP mayor a 0."""
    return p["hp"] > 0


def calcular_daño(atacante, defensor):
    """
    Fórmula del proyecto: daño = ATK atacante - DEF defensor.
    Si el resultado es menor a 1, se asigna el daño mínimo de 1.
    """
    daño = atacante["atk"] - defensor["def"]
    if daño < 1:
        return 1
    return daño


def todos_ko(equipo, indice):
    """
    revisa si todos los personajes esten ko
    """
    if indice >= len(equipo):
        return True
    if esta_vivo(equipo[indice]):
        return False
    return todos_ko(equipo, indice + 1)


def buscar_vivo(equipo, indice):
    """
    se fija en el proximo personaje despues del que murio
    """
    if indice >= len(equipo):
        return None
    if esta_vivo(equipo[indice]):
        return equipo[indice]
    return buscar_vivo(equipo, indice + 1)


def restaurar_equipo(equipo, indice):
    """
    restaura la vida de los personajes 
    """
    if indice >= len(equipo):
        return
    restaurar_vida(equipo[indice])
    restaurar_equipo(equipo, indice + 1)


def construir_equipo(indices, pos):
    """
    RECURSIÓN: construye una lista de copias de personajes a partir
    de una lista de índices. Caso base: pos >= cantidad de índices.
    """
    if pos >= len(indices):
        return []
    personaje = copiar_personaje(PERSONAJES[indices[pos]])
    return [personaje] + construir_equipo(indices, pos + 1)


def copiar_lista(lista, indice):
    """
    devuelve una copia del equipo que se eligio para no afectar el diccionario
    """
    if indice >= len(lista):
        return []
    return [copiar_personaje(lista[indice])] + copiar_lista(lista, indice + 1)


def jugador_ya_tiene(nombre_personaje, indice):
    """
    se fija que el personaje que derrotamos no es uno que ya tenemos para no tenerlo repetido
    """
    if indice >= len(equipo_jugador):
        return False
    if equipo_jugador[indice]["nombre"] == nombre_personaje:
        return True
    return jugador_ya_tiene(nombre_personaje, indice + 1)


def transferir_personaje(personaje, equipo_origen, equipo_destino):
    """
   mueve un personaje de un equipo al otro
    """
    equipo_origen.remove(personaje)
    if equipo_destino is equipo_jugador and jugador_ya_tiene(personaje["nombre"], 0):
        return   # ya lo tiene, no duplicar
    restaurar_vida(personaje)
    equipo_destino.append(personaje)

# ==============================================================
# SECCIÓN 2 — FUNCIONES DE VALIDACIÓN
# ==============================================================

def mostrar_error(mensaje):
    """Muestra una ventana emergente con el mensaje de error."""
    messagebox.showerror("Error", mensaje)


def validar_nombre(texto):
    """
    Valida que el nombre no esté vacío, tenga máximo 20 caracteres
    y solo contenga letras y espacios.
    Retorna True si es válido, False si no lo es.
    """
    if len(texto.strip()) == 0:
        mostrar_error("El nombre no puede estar vacío.")
        return False
    if len(texto.strip()) > 20:
        mostrar_error("El nombre no puede tener más de 20 caracteres.")
        return False
    if not texto.strip().replace(" ", "").isalpha():
        mostrar_error("El nombre solo puede tener letras y espacios.")
        return False
    return True


def validar_seleccion_personajes(nombres):
    """
    esta funcion valida que se hayan elegido 3 personajes diferentes
    """
    eleccion = "— elige un personaje —"
    if nombres[0] == eleccion or nombres[1] == eleccion or nombres[2] == eleccion:
        mostrar_error("Debes elegir un personaje en cada ranura.")
        return False
    if len(set(nombres)) != 3:
        mostrar_error("No puedes elegir el mismo personaje dos veces.")
        return False
    return True


def validar_cambio_personaje(personaje):
    """
    valida que el personaje que se elige en batalla este vivo y no sea el mismo que esta luchando
    """
    if not esta_vivo(personaje):
        mostrar_error("Ese personaje está en KO, elige otro.")
        return False
    if personaje == personaje_activo_jugador:
        mostrar_error("Ese personaje ya está en batalla.")
        return False
    return True

# ==============================================================
# SECCIÓN 3 — LÓGICA DEL JUEGO
# ==============================================================

def armar_equipo_hollow():
    """Elige 3 personajes al azar de la lista y devuelve copias."""
    seleccion = random.sample(PERSONAJES, 3)
    return copiar_lista(seleccion, 0)


def hollow_decide():
    """
    decisiones del hollow
    """
    return random.choice(["atacar", "atacar", "atacar", "cambiar"])


def ejecutar_turno(atacante, defensor, es_turno_jugador):
    """
    esta funcion decide quien ataca y cuanto daño hace uno al otro
    """
    global turno_en_progreso

    if not esta_vivo(atacante) or not esta_vivo(defensor):
        _manejar_ko(es_turno_jugador)
        return

    # Calcular y aplicar daño
    daño = calcular_daño(atacante, defensor)
    defensor["hp"] -= daño
    if defensor["hp"] < 0:
        defensor["hp"] = 0

    actualizar_pantalla_batalla()

    ventana.after(1200, lambda: _continuar_turno(es_turno_jugador))

def _continuar_turno(fue_turno_jugador):
    """
    nos fijamos si al atacar uno termina ko y si no sigue
    """
    global turno_en_progreso

    if fue_turno_jugador:
        # si el jugador atacó revisamos si el hollow quedó en KO
        if not esta_vivo(personaje_activo_hollow):
            _manejar_ko(True)
            return
        # si el hollow sigue vivo, ahora ataca el hollow
        _turno_hollow()
    else:
        # si el hollow atacó revisamos si el jugador quedó en KO
        if not esta_vivo(personaje_activo_jugador):
            _manejar_ko(False)
            return
        # si el jugador sigue vivo devolvemos el turno al jugador
        turno_en_progreso = False
        if btn_atacar:
            btn_atacar.config(state="normal")


def _turno_hollow():
    """Decide la acción del Hollow y la ejecuta"""
    global personaje_activo_hollow

    accion = hollow_decide()

    if accion == "cambiar":
        nuevo = buscar_vivo(equipo_hollow, 0)
        if nuevo is not None and nuevo != personaje_activo_hollow:
            personaje_activo_hollow = nuevo
            actualizar_pantalla_batalla()

    ventana.after(800, lambda: ejecutar_turno(
        personaje_activo_hollow,
        personaje_activo_jugador,
        False
    ))


def _manejar_ko(gano_el_jugador):
    """
    esta funcion administra el ko de un personaje, transfiere al ganador el personaje derrotado, 
    actualiza el puntaje y decide si la batalla terminó.
    """
    global personaje_activo_jugador, personaje_activo_hollow
    global puntaje_jugador, puntaje_hollow, turno_en_progreso

    if gano_el_jugador:
        puntaje_jugador += 1
        transferir_personaje(personaje_activo_hollow, equipo_hollow, equipo_jugador)
        if todos_ko(equipo_hollow, 0):
            turno_en_progreso = False
            terminar_batalla(True)
            return
        personaje_activo_hollow = buscar_vivo(equipo_hollow, 0)
    else:
        puntaje_hollow += 1
        transferir_personaje(personaje_activo_jugador, equipo_jugador, equipo_hollow)
        if todos_ko(equipo_jugador, 0):
            turno_en_progreso = False
            terminar_batalla(False)
            return
        personaje_activo_jugador = buscar_vivo(equipo_jugador, 0)

    actualizar_pantalla_batalla()
    turno_en_progreso = False
    if btn_atacar:
        btn_atacar.config(state="normal")

# ==============================================================
# SECCIÓN 4 — PANTALLA TKINTER
# ==============================================================

def limpiar_ventana():
    """
    elimina la ventana que esta abierta para crear una nueva
    """
    anterior = ventana.winfo_children()
    if len(anterior) == 0:
        return
    anterior[0].destroy()
    limpiar_ventana()   # ← llamada recursiva


# ── PANTALLA DE INICIO ─────────────────────────────────────────

def mostrar_inicio():
    # crea la pantalla inicial: nombre y selección de personajes.
    limpiar_ventana()

    ventana.title("Imaginary Battle — Inicio")
    ventana.geometry("680x580")
    ventana.configure(bg="#1a1a2e")
    ventana.resizable(False, False)

    # Título
    tk.Label(ventana, text="⚔  IMAGINARY BATTLE  ⚔",
             font=("Arial", 20, "bold"), bg="#1a1a2e", fg="#e94560").pack(pady=(20, 2))
    tk.Label(ventana, text="Guardián de las Historias",
             font=("Arial", 11), bg="#1a1a2e", fg="#a8a8b3").pack(pady=(0, 12))

    # Contenedor principal
    frame = tk.Frame(ventana, bg="#16213e", bd=2, relief="groove")
    frame.pack(padx=30, fill="x")

    # ── Nombre ───────────────────────────────────────────────
    tk.Label(frame, text="Tu nombre:", font=("Arial", 11, "bold"),
             bg="#16213e", fg="white").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

    entrada_nombre = tk.Entry(frame, font=("Arial", 11), width=24,
                              bg="#0f3460", fg="white", insertbackground="white", bd=0)
    entrada_nombre.grid(row=0, column=1, padx=15, pady=(15, 5))

    # ── Selección de personajes ───────────────────────────────
    tk.Label(frame, text="Elige 3 personajes:", font=("Arial", 11, "bold"),
             bg="#16213e", fg="white").grid(row=1, column=0, sticky="nw", padx=15, pady=8)

    frame_slots = tk.Frame(frame, bg="#16213e")
    frame_slots.grid(row=1, column=1, padx=15, pady=8, sticky="w")

    opciones    = construir_opciones_menu(0)   # ← recursiva
    placeholder = "— elige un personaje —"

    var_slot1 = tk.StringVar(value=placeholder)
    var_slot2 = tk.StringVar(value=placeholder)
    var_slot3 = tk.StringVar(value=placeholder)

    tk.Label(frame_slots, text="Ranura 1:", font=("Arial", 10),
             bg="#16213e", fg="#a8a8b3").grid(row=0, column=0, sticky="w", pady=3)
    om1 = tk.OptionMenu(frame_slots, var_slot1, *opciones)
    om1.config(bg="#e94560", fg="white", font=("Arial", 10), bd=0,
               activebackground="#c73652", activeforeground="white",
               highlightthickness=0)
    om1["menu"].config(bg="#e94560", fg="white", font=("Arial", 10))
    om1.grid(row=0, column=1, sticky="w", padx=6, pady=3)

    tk.Label(frame_slots, text="Ranura 2:", font=("Arial", 10),
             bg="#16213e", fg="#a8a8b3").grid(row=1, column=0, sticky="w", pady=3)
    om2 = tk.OptionMenu(frame_slots, var_slot2, *opciones)
    om2.config(bg="#e94560", fg="white", font=("Arial", 10), bd=0,
               activebackground="#c73652", activeforeground="white",
               highlightthickness=0)
    om2["menu"].config(bg="#e94560", fg="white", font=("Arial", 10))
    om2.grid(row=1, column=1, sticky="w", padx=6, pady=3)

    tk.Label(frame_slots, text="Ranura 3:", font=("Arial", 10),
             bg="#16213e", fg="#a8a8b3").grid(row=2, column=0, sticky="w", pady=3)
    om3 = tk.OptionMenu(frame_slots, var_slot3, *opciones)
    om3.config(bg="#e94560", fg="white", font=("Arial", 10), bd=0,
               activebackground="#c73652", activeforeground="white",
               highlightthickness=0)
    om3["menu"].config(bg="#e94560", fg="white", font=("Arial", 10))
    om3.grid(row=2, column=1, sticky="w", padx=6, pady=3)

    # Guardar las 3 variables en una lista para pasarlas al botón
    vars_slots = [var_slot1, var_slot2, var_slot3]

    # ── Botones ───────────────────────────────────────────────
    btn_frame = tk.Frame(ventana, bg="#1a1a2e")
    btn_frame.pack(pady=18)

    tk.Button(btn_frame, text="  INICIAR  ", font=("Arial", 13, "bold"),
              bg="#e94560", fg="white", padx=10, pady=8, bd=0, cursor="hand2",
              command=lambda: al_presionar_iniciar(entrada_nombre, vars_slots)
              ).pack(side="left", padx=10)

    tk.Button(btn_frame, text="  ABOUT  ", font=("Arial", 13, "bold"),
              bg="#0f3460", fg="white", padx=10, pady=8, bd=0, cursor="hand2",
              command=mostrar_about
              ).pack(side="left", padx=10)


def construir_opciones_menu(indice):
    """
    muestra las caracteristicas de los personajes en el juego
    """
    if indice >= len(PERSONAJES):
        return []
    p = PERSONAJES[indice]
    texto = f"{p['nombre']:<12}  HP:{p['hp_max']:>3}  ATK:{p['atk']:>2}  DEF:{p['def']:>2}"
    return [texto] + construir_opciones_menu(indice + 1)


def al_presionar_iniciar(entrada_nombre, vars_slots):
    """Valida todos los campos y arranca el juego si todo está correcto."""
    global nombre_jugador, equipo_jugador

    nombre   = entrada_nombre.get()
    nombres  = [vars_slots[0].get(), vars_slots[1].get(), vars_slots[2].get()]

    if not validar_nombre(nombre):
        return
    if not validar_seleccion_personajes(nombres):
        return

    nombre_jugador = nombre.strip()

    # Convertir los nombres elegidos a índices para construir_equipo
    indices = buscar_indices_por_nombres(nombres, 0, [])
    equipo_jugador = construir_equipo(indices, 0)

    mostrar_mapa()


def buscar_indices_por_nombres(nombres, indice, resultado):
    """
    convierte el nombre del personaje en el indice que tiene en la lista personajes
    """
    if indice >= len(nombres):
        return resultado
    nombre_buscado = nombres[indice].split()[0]   
    id = encontrar_indice_personaje(nombre_buscado, 0)
    return buscar_indices_por_nombres(nombres, indice + 1, resultado + [id])


def encontrar_indice_personaje(nombre_buscado, indice):
    """
    busca el indice de un personaje en la lista personajes y lo devuelve para saber cual personaje es
    """
    if indice >= len(PERSONAJES):
        return 0
    if PERSONAJES[indice]["nombre"] == nombre_buscado:
        return indice
    return encontrar_indice_personaje(nombre_buscado, indice + 1)


def mostrar_about():
    """Muestra la información del proyecto en una ventana nueva."""
    messagebox.showinfo("About — Imaginary Battle",
        "Imaginary Battle\n\n"
        "Proyecto 1 — Introducción a la Programación\n"
        "Tecnológico de Costa Rica · I Semestre 2026\n\n"
        "Profesor: Santiago Ramírez\n"
        "Creador: Jefferson Cerdas Porras\n\n"
        "Carnet: 2025075834\n\n"
        "Desarrollado con Python 3 y Tkinter.\n"
        "Derrota a los 5 Hollows para ganar."
    )


# ── PANTALLA DE MAPA ───────────────────────────────────────────

def mostrar_mapa():
    """Dibuja el mapa visual con nodos conectados y el progreso del jugador."""
    limpiar_ventana()
    ventana.title("Imaginary Battle — Mapa")
    ventana.geometry("680x500")
    ventana.configure(bg="#1a1a2e")

    tk.Label(ventana, text="MAPA DE FRAGMENTOS",
             font=("Arial", 18, "bold"), bg="#1a1a2e", fg="#e94560").pack(pady=(20, 2))
    tk.Label(ventana,
             text=f"Guardian: {nombre_jugador}   |   Hollows derrotados: {huecos_derrotados} / 5",
             font=("Arial", 11), bg="#1a1a2e", fg="#a8a8b3").pack(pady=(0, 8))

    # Canvas donde se dibuja el mapa
    canvas = tk.Canvas(ventana, width=620, height=340, bg="#0d1b2a",
                       highlightthickness=0)
    canvas.pack(padx=30)

    # Posiciones de cada nodo en el canvas
    nodos_x = [80, 190, 310, 430, 540]
    nodos_y = [170, 90,  200, 100, 170]

    dibujar_caminos(canvas, nodos_x, nodos_y, 0)   # ← recursiva
    dibujar_nodos(canvas, nodos_x, nodos_y, 0)      # ← recursiva


def dibujar_caminos(canvas, xs, ys, indice):
    """
    RECURSIÓN: dibuja la línea que conecta cada nodo con el siguiente.
    Caso base: no hay más pares de nodos que conectar.
    """
    if indice >= len(xs) - 1:
        return
    color = "#2d5a27" if indice < huecos_derrotados else "#3a4a6b"
    canvas.create_line(xs[indice], ys[indice], xs[indice + 1], ys[indice + 1],
                       fill=color, width=4, dash=(8, 4))
    dibujar_caminos(canvas, xs, ys, indice + 1)


def dibujar_nodos(canvas, xs, ys, indice):
    """
    dibuja los nodos de los mapas y los cambia de color segun se logre derrotar a los hollow o no
    """
    if indice >= len(UBICACIONES):
        return

    x = xs[indice]
    y = ys[indice]
    ya_derrotado = indice < huecos_derrotados
    es_siguiente  = indice == huecos_derrotados

    if ya_derrotado:
        color_circulo = "#2d5a27"
        color_borde   = "#4ade80"
        simbolo       = "OK"
        color_texto   = "#4ade80"
    elif es_siguiente:
        color_circulo = "#7a1a2e"
        color_borde   = "#e94560"
        simbolo       = "!"
        color_texto   = "white"
    else:
        color_circulo = "#1a2a4a"
        color_borde   = "#3a4a6b"
        simbolo       = "?"
        color_texto   = "#6b7a9b"

    # Sombra
    canvas.create_oval(x - 28, y - 28, x + 28, y + 28,
                       fill="#000000", outline="")
    # Círculo del nodo
    canvas.create_oval(x - 26, y - 26, x + 26, y + 26,
                       fill=color_circulo, outline=color_borde, width=2)
    # Símbolo dentro del nodo
    canvas.create_text(x, y, text=simbolo,
                       font=("Arial", 11, "bold"), fill=color_texto)
    # Nombre de la ubicación
    canvas.create_text(x, y + 42, text=UBICACIONES[indice],
                       font=("Arial", 9, "bold"), fill=color_texto)
    # Número del hollow
    canvas.create_text(x, y - 42, text=f"Hollow {indice + 1}",
                       font=("Arial", 8), fill=color_texto)

    # Solo el nodo siguiente es clickeable
    if es_siguiente:
        area = canvas.create_oval(x - 26, y - 26, x + 26, y + 26,
                                  fill="", outline="", width=0)
        canvas.tag_bind(area, "<Button-1>",
                        lambda e, i=indice: al_entrar_ubicacion(i))
        canvas.tag_bind(area, "<Enter>",
                        lambda e: canvas.config(cursor="hand2"))
        canvas.tag_bind(area, "<Leave>",
                        lambda e: canvas.config(cursor=""))

        # Botón de texto debajo del canvas para mayor claridad
        tk.Button(ventana,
                  text=f"Entrar a {UBICACIONES[indice]}",
                  font=("Arial", 11, "bold"),
                  bg="#e94560", fg="white", padx=16, pady=6, bd=0,
                  cursor="hand2",
                  command=lambda i=indice: al_entrar_ubicacion(i)
                  ).pack(pady=(10, 0))

    dibujar_nodos(canvas, xs, ys, indice + 1)


def al_entrar_ubicacion(indice):
    """Prepara el equipo del Hollow y abre la pantalla de batalla."""
    global equipo_hollow, personaje_activo_jugador, personaje_activo_hollow
    global puntaje_jugador, puntaje_hollow

    # Restaurar equipo del jugador al inicio de cada batalla
    restaurar_equipo(equipo_jugador, 0) 

    equipo_hollow = armar_equipo_hollow()
    personaje_activo_jugador = equipo_jugador[0]
    personaje_activo_hollow = equipo_hollow[0]
    puntaje_jugador = 0
    puntaje_hollow = 0

    mostrar_batalla()


# ── PANTALLA DE BATALLA ────────────────────────────────────────

def mostrar_batalla():
    """Dibuja la pantalla de combate completa."""
    global lbl_img_jugador, lbl_img_hollow, img_jugador_tk, img_hollow_tk
    global lbl_hp_jugador, lbl_hp_hollow, lbl_puntaje
    global lbl_nombre_pj, lbl_nombre_hollow, lbl_stats_jugador, lbl_stats_hollow, btn_atacar
    global turno_en_progreso

    turno_en_progreso = False
    limpiar_ventana()
    ventana.title("Imaginary Battle — Batalla")
    ventana.geometry("680x580")
    ventana.configure(bg="#1a1a2e")

    # Puntaje 
    lbl_puntaje = tk.Label(ventana,
        text=f"Puntaje  —  Tu: {puntaje_jugador}   |   Hollow: {puntaje_hollow}",
        font=("Arial", 12), bg="#1a1a2e", fg="#e94560")
    lbl_puntaje.pack(pady=(15, 6))

    # Arena de batalla 
    arena = tk.Frame(ventana, bg="#16213e", bd=2, relief="groove")
    arena.pack(padx=30, fill="x")

    # Personaje del jugador
    frame_j = tk.Frame(arena, bg="#16213e")
    frame_j.pack(side="left", expand=True, padx=20, pady=12)
    tk.Label(frame_j, text=nombre_jugador,
             font=("Arial", 9), bg="#16213e", fg="#a8a8b3").pack()
    lbl_nombre_pj = tk.Label(frame_j,
        text=personaje_activo_jugador["nombre"],
        font=("Arial", 13, "bold"), bg="#16213e", fg="white")
    lbl_nombre_pj.pack()
    img_jugador_tk = cargar_imagen(personaje_activo_jugador["img"])
    lbl_img_jugador = tk.Label(frame_j, bg="#16213e",
        image=img_jugador_tk,
        text="" if img_jugador_tk else "[ sin imagen ]",
        fg="#a8a8b3", font=("Arial", 9))
    lbl_img_jugador.pack(pady=4)
    lbl_hp_jugador = tk.Label(frame_j,
        text=f"HP: {personaje_activo_jugador['hp']} / {personaje_activo_jugador['hp_max']}",
        font=("Arial", 11), bg="#16213e", fg="#4ade80")
    lbl_hp_jugador.pack()
    lbl_stats_jugador = tk.Label(frame_j,
        text=f"ATK {personaje_activo_jugador['atk']}  DEF {personaje_activo_jugador['def']}",
        font=("Arial", 9), bg="#16213e", fg="#a8a8b3")
    lbl_stats_jugador.pack()

    # VS
    tk.Label(arena, text="VS", font=("Arial", 22, "bold"),
             bg="#16213e", fg="#e94560").pack(side="left", padx=15)

    # Personaje del Hollow 
    frame_h = tk.Frame(arena, bg="#16213e")
    frame_h.pack(side="right", expand=True, padx=20, pady=12)
    tk.Label(frame_h, text="HOLLOW",
             font=("Arial", 9), bg="#16213e", fg="#a8a8b3").pack()
    lbl_nombre_hollow = tk.Label(frame_h,
        text=personaje_activo_hollow["nombre"],
        font=("Arial", 13, "bold"), bg="#16213e", fg="white")
    lbl_nombre_hollow.pack()
    img_hollow_tk = cargar_imagen(personaje_activo_hollow["img"])
    lbl_img_hollow = tk.Label(frame_h, bg="#16213e",
        image=img_hollow_tk,
        text="" if img_hollow_tk else "[ sin imagen ]",
        fg="#a8a8b3", font=("Arial", 9))
    lbl_img_hollow.pack(pady=4)
    lbl_hp_hollow = tk.Label(frame_h,
        text=f"HP: {personaje_activo_hollow['hp']} / {personaje_activo_hollow['hp_max']}",
        font=("Arial", 11), bg="#16213e", fg="#f87171")
    lbl_hp_hollow.pack()
    lbl_stats_hollow = tk.Label(frame_h,
        text=f"ATK {personaje_activo_hollow['atk']}  DEF {personaje_activo_hollow['def']}",
        font=("Arial", 9), bg="#16213e", fg="#a8a8b3")
    lbl_stats_hollow.pack()

    # ── Equipo del jugador ────────────────────────────────────
    tk.Label(ventana, text="Tu equipo:",
             font=("Arial", 10), bg="#1a1a2e", fg="#a8a8b3").pack(pady=(12, 2))
    frame_equipo = tk.Frame(ventana, bg="#1a1a2e")
    frame_equipo.pack()
    mostrar_equipo_en_batalla(frame_equipo, equipo_jugador, 0)   # ← recursiva

    # ── Botones de acción ─────────────────────────────────────
    frame_btns = tk.Frame(ventana, bg="#1a1a2e")
    frame_btns.pack(pady=16)

    btn_atacar = tk.Button(frame_btns, text="ATACAR",
                           font=("Arial", 13, "bold"),
                           bg="#e94560", fg="white", padx=18, pady=8, bd=0,
                           cursor="hand2", command=al_presionar_atacar)
    btn_atacar.pack(side="left", padx=10)

    tk.Button(frame_btns, text="CAMBIAR",
              font=("Arial", 13, "bold"),
              bg="#0f3460", fg="white", padx=18, pady=8, bd=0,
              cursor="hand2", command=al_presionar_cambiar).pack(side="left", padx=10)


def mostrar_equipo_en_batalla(frame, equipo, indice):
    """
    muestra el nombre del equipo y muestra si esta ko o ok
    """
    if indice >= len(equipo):
        return
    p     = equipo[indice]
    if esta_vivo(p):
        color = "#4ade80"
        texto = p["nombre"]
    else:
        color = "#6b7280"
        texto = f"{p['nombre']} (KO)"
    tk.Label(frame, text=texto, font=("Arial", 9),
             bg="#1a1a2e", fg=color).pack(side="left", padx=8)
    mostrar_equipo_en_batalla(frame, equipo, indice + 1)


def actualizar_pantalla_batalla():
    """Refresca los labels de HP, ATK, DEF, imágenes, nombres y puntaje sin redibujar toda la pantalla."""
    global img_jugador_tk, img_hollow_tk

    if lbl_hp_jugador:
        lbl_hp_jugador.config(
            text=f"HP: {personaje_activo_jugador['hp']} / {personaje_activo_jugador['hp_max']}")
    if lbl_hp_hollow:
        lbl_hp_hollow.config(
            text=f"HP: {personaje_activo_hollow['hp']} / {personaje_activo_hollow['hp_max']}")
    if lbl_puntaje:
        lbl_puntaje.config(
            text=f"Puntaje  —  Tu: {puntaje_jugador}   |   Hollow: {puntaje_hollow}")
    if lbl_nombre_pj:
        lbl_nombre_pj.config(text=personaje_activo_jugador["nombre"])
    if lbl_nombre_hollow:
        lbl_nombre_hollow.config(text=personaje_activo_hollow["nombre"])
    if lbl_stats_jugador:
        lbl_stats_jugador.config(
            text=f"ATK {personaje_activo_jugador['atk']}  DEF {personaje_activo_jugador['def']}")
    if lbl_stats_hollow:
        lbl_stats_hollow.config(
            text=f"ATK {personaje_activo_hollow['atk']}  DEF {personaje_activo_hollow['def']}")
    # Actualizar imagen del jugador, se guarda en global para evitar que el recolector de basura de Python la borre de memoria
    if lbl_img_jugador:
        img_jugador_tk = cargar_imagen(personaje_activo_jugador["img"])
        if img_jugador_tk:
            lbl_img_jugador.config(image=img_jugador_tk, text="")
        else:
            lbl_img_jugador.config(image="", text="[ sin imagen ]")
    # Actualizar imagen del hollow
    if lbl_img_hollow:
        img_hollow_tk = cargar_imagen(personaje_activo_hollow["img"])
        if img_hollow_tk:
            lbl_img_hollow.config(image=img_hollow_tk, text="")
        else:
            lbl_img_hollow.config(image="", text="[ sin imagen ]")


def al_presionar_atacar():
    """Inicia el turno del jugador cuando presiona el botón ATACAR."""
    global turno_en_progreso
    if turno_en_progreso:
        return
    turno_en_progreso = True
    btn_atacar.config(state="disabled")
    ejecutar_turno(personaje_activo_jugador, personaje_activo_hollow, True)


def al_presionar_cambiar():
    # Abre la ventana para cambiar personaje
    # Si el turno está en progreso no se puede cambiar
    if turno_en_progreso:
        mostrar_error("Espera a que termine el turno antes de cambiar.")
        return

    # Crear ventana secundaria del cambio de personaje
    ventana_cambio = tk.Toplevel(ventana)
    ventana_cambio.title("Cambiar personaje")
    ventana_cambio.configure(bg="#1a1a2e")
    ventana_cambio.resizable(False, False)

    tk.Label(ventana_cambio, text="Elige un personaje:",
             font=("Arial", 12, "bold"), bg="#1a1a2e", fg="white").pack(pady=12)

    # Scrollbar por si hay muchos personajes que se pueda hacer scroll
    canvas_scroll = tk.Canvas(ventana_cambio, bg="#1a1a2e", highlightthickness=0, width=300)
    scrollbar     = tk.Scrollbar(ventana_cambio, orient="vertical",
                                 command=canvas_scroll.yview)
    canvas_scroll.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas_scroll.pack(side="left", fill="both", expand=True)

    # Frame adentro del canvas donde van los botones
    frame_opciones = tk.Frame(canvas_scroll, bg="#1a1a2e")
    ventana_id = canvas_scroll.create_window((0, 0), window=frame_opciones, anchor="nw")

    # Mostrar todos los personajes vivos
    mostrar_opciones_cambio(frame_opciones, equipo_jugador, 0, ventana_cambio)

    # Ajustar el área de scroll y el alto de la ventana según cuántos botones haya
    frame_opciones.update_idletasks()
    alto_contenido = frame_opciones.winfo_reqheight()
    alto_ventana   = min(alto_contenido + 80, 420)  
    canvas_scroll.configure(height=alto_contenido)
    ventana_cambio.geometry(f"320x{alto_ventana}")


def mostrar_opciones_cambio(frame, equipo, indice, ventana_cambio):
    if indice >= len(equipo):
        return

    p = equipo[indice]

    # Solo mostrar personajes que estén vivos y no sean el que ya está peleando
    if esta_vivo(p) and p != personaje_activo_jugador:
        tk.Button(frame,
                  text=f"{p['nombre']}   HP:{p['hp']}/{p['hp_max']}",
                  font=("Arial", 11), bg="#0f3460", fg="white",
                  padx=10, pady=6, bd=0, cursor="hand2",
                  command=lambda per=p: confirmar_cambio(per, ventana_cambio)
                  ).pack(pady=4, padx=20, fill="x")
    mostrar_opciones_cambio(frame, equipo, indice + 1, ventana_cambio)


def confirmar_cambio(personaje, ventana_cambio):
    """Valida el cambio de personaje y lo aplica si es correcto."""
    global personaje_activo_jugador
    if not validar_cambio_personaje(personaje):
        return
    personaje_activo_jugador = personaje
    ventana_cambio.destroy()
    actualizar_pantalla_batalla()


def terminar_batalla(gano_jugador):
    """Procesa el resultado de la batalla y decide la siguiente pantalla."""
    global huecos_derrotados

    if gano_jugador:
        huecos_derrotados += 1
        messagebox.showinfo("Victoria!",
            f"Derrotaste al Hollow de {UBICACIONES[huecos_derrotados - 1]}!\n"
            f"Personajes capturados: {puntaje_jugador}")
        if huecos_derrotados >= 5:
            mostrar_fin_juego(True)
        else:
            mostrar_mapa()
    else:
        messagebox.showinfo("Derrota")
        mostrar_fin_juego(False)


# PANTALLA DE FIN 

def mostrar_fin_juego(gano):
    # Muestra la pantalla final de victoria o derrota.
    limpiar_ventana()
    ventana.title("Imaginary Battle — Fin")
    ventana.geometry("500x340")
    ventana.configure(bg="#1a1a2e")

    if gano:
        titulo  = "🏆  ¡VICTORIA TOTAL!"
        mensaje = (f"Felicidades, {nombre_jugador}!\n"
                   "Los 5 Hollows han sido derrotados.")
        color   = "#4ade80"
    else:
        titulo  = "💀  DERROTA"
        mensaje = ("Los Hollows fueron demasiado poderosos.\n")
        color   = "#f87171"

    tk.Label(ventana, text=titulo,
             font=("Arial", 22, "bold"), bg="#1a1a2e", fg=color).pack(pady=(55, 16))
    tk.Label(ventana, text=mensaje,
             font=("Arial", 13), bg="#1a1a2e", fg="white", justify="center").pack()
    tk.Button(ventana, text="  Jugar de nuevo  ",
              font=("Arial", 12, "bold"),
              bg="#e94560", fg="white", padx=10, pady=8, bd=0,
              cursor="hand2", command=reiniciar_juego).pack(pady=28)


def reiniciar_juego():
    """Reinicia todas las variables globales y vuelve a la pantalla de inicio."""
    global nombre_jugador, equipo_jugador, equipo_hollow
    global puntaje_jugador, puntaje_hollow, huecos_derrotados
    global personaje_activo_jugador, personaje_activo_hollow, turno_en_progreso

    nombre_jugador           = ""
    equipo_jugador           = []
    equipo_hollow            = []
    puntaje_jugador          = 0
    puntaje_hollow           = 0
    huecos_derrotados        = 0
    personaje_activo_jugador = None
    personaje_activo_hollow  = None
    turno_en_progreso        = False

    mostrar_inicio()

# ==============================================================
# SECCIÓN 5 — ARRANCAR EL JUEGO
# ==============================================================

ventana = tk.Tk()
mostrar_inicio()
ventana.mainloop()