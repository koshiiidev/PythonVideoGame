"""
Nivel: adentro de la casona

Dos puertas: la de abajo devuelve al pueblo y la de arriba baja a la mazmorra.

Leyenda
    .  piso de madera (viene de SUELO, no hace falta ponerlo en el array)
    M  muro    autotileado, el mismo juego de tiles que el del pueblo
    O  barril  J  tinaja   T  tronco
    P  puerta (no bloquea)
    D  comedor        E  estante con comida     e  estante vacio
    L  alfombra (va en DECOR: es plana, se pisa y no estorba)
    c cama
"""

TITULO = 'La casona'

# Debajo de todo va este tile en vez del pasto: es un interior
SUELO = 'assets/tiles/tile_piso.png'

MAPA = [
    ".......................",
    "MMMMMMMMMMMPMMMMMMMMMMM",
    "MJE.e.e.e........JO...M",
    "M.O.................c.M",
    "M.....................M",
    "M...T.............T...M",
    "M......D..............M",
    "M.O.................O.M",
    "M.....................M",
    "MMMMMMMMMMMPMMMMMMMMMMM",
    ".......................",
]

# ----------------------------------------------------------------------------
# CAPA DE ENCIMA
# ----------------------------------------------------------------------------
# El hueco es el ESPACIO ' ', no el punto. Aqui va la alfombra: esta TIRADA en
# el piso, asi que no puede ir en MAPA compitiendo por la casilla con el
# comedor ni con nada. Se dibuja debajo de los personajes (ver PLANOS).
DECOR = [
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
]

TERRENOS = {'M': 'muro'}

# La puerta esta EMPOTRADA en el muro: sin esto el muro veria un hueco y se
# rematarian los dos lados, como si la pared se cortara ahi
CONTINUAN = {'M': 'P'}

OBJETOS = {
    'T': 'assets/tiles/tile_tronco1.png',
    'P': 'assets/tiles/puerta_muro.png',
    'O': 'assets/tiles/tile_barril.png',
    'J': 'assets/tiles/tile_tinaja.png',
    # Muebles
    'D': 'assets/tiles/comedor.png',
    'E': 'assets/tiles/estante1.png',
    'e': 'assets/tiles/estante2.png',
    'L': 'assets/tiles/alfombra.png',
    'c': 'assets/tiles/cama.png',
}

# La alfombra NO va aca: se pisa
SOLIDOS = {'M', 'O', 'J', 'T', 'D', 'E', 'e', 'c'}

# COMO SE DIBUJA: ancho en tiles. El alto sale de la proporcion del PNG
ALTOS = {'D': 3.0, 'E': 2.0, 'e': 2.0, 'L': 2.0, 'c': 2.0}

# CUANTAS CASILLAS OCUPA: los muebles miden dos tiles de ancho, asi que sin
# esto bloquearian solo la casilla de su letra y se podria caminar por encima
# de la mitad del mueble
HUELLAS = {'D': (3, 3), 'E': (2, 2), 'e': (2, 2), 'c': (2, 2)}

# PLANOS: Se dibuja debajo de lospersonajes y no entra al orden por profundidad
PLANOS = {'L'}

# Las CAJAS de colision (proporciones del tile) las pone Luis en
# config.settings.COLISIONES, o aqui mismo con un COLISIONES propio si estos
# muebles necesitan una medida distinta de la comun

JUGADOR_INICIO = (11, 8)
MUSICA = 'casa.ogg'
OBJETIVO = 3
ES_FINAL = False

NPCS = [
    {'sprite': 'npc_F_6.png', 'x': 2, 'y': 5, 'solido': True},
]

SALIDAS = {
    (11, 9): ('pueblo', 7, 20),    # puerta de abajo: de vuelta al pueblo
    (11, 1): ('mazmorra', 7, 7),   # puerta de arriba: baja a la mazmorra
}
