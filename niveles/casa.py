"""
Nivel: adentro de la casona

Dos puertas: la de abajo devuelve al pueblo y la de arriba baja a la mazmorra.

Leyenda
    .  piso de madera (viene de SUELO, no hace falta ponerlo en el array)
    M  muro    autotileado, el mismo juego de tiles que el del pueblo
    O  barril  J  tinaja   T  tronco
    P  puerta (no bloquea)
"""

TITULO = 'La casona'

# Debajo de todo va este tile en vez del pasto: es un interior
SUELO = 'assets/tiles/tile_piso.png'

MAPA = [
    "MMMMMMMMPMMMMMMMM",
    "M...............M",
    "M.OJ.........JO.M",
    "M...............M",
    "M...T.......T...M",
    "M...............M",
    "M.O...........O.M",
    "M...............M",
    "MMMMMMMMPMMMMMMMM",
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
}

SOLIDOS = {'M', 'O', 'J', 'T'}

JUGADOR_INICIO = (8, 7)
MUSICA = 'casa.ogg'
OBJETIVO = 3
ES_FINAL = False

NPCS = [
    {'sprite': 'npc_F_6.png', 'x': 2, 'y': 5, 'solido': True},
]

SALIDAS = {
    (8, 8): ('pueblo', 7, 20),    # puerta de abajo: de vuelta al pueblo
    (8, 0): ('mazmorra', 7, 7),   # puerta de arriba: baja a la mazmorra
}
