# -*- coding: utf-8 -*-
"""
Nivel: la mazmorra bajo la casona. Es el ultimo, aqui espera el jefe.

Leyenda
    .  piso de piedra (viene de SUELO)
    M  muro    autotileado, el mismo juego de tiles que el del pueblo
    Z  antorcha (animada)      O  barril      J  tinaja
    P  puerta (no bloquea): devuelve al pueblo
"""

TITULO = 'La mazmorra'

# El piso se pinta debajo de todo, en vez del pasto
SUELO = 'assets/tiles/tile_muro_mazmorra.png'

MAPA = [
    "MMMMMMMMMMMMMMMMMMMMMMMMM",
    "M.......................M",
    "M.Z.........Z........Z..M",
    "M.......................M",
    "M...O......J.......O....M",
    "M.......................M",
    "M.Z.......MMMMM......Z..M",
    "M.........M...M.........M",
    "M....J....MM.MM.....O...M",
    "M.......................M",
    "MMMMMMMMMMMPMMMMMMMMMMMMM",
]

TERRENOS = {'M': 'muro'}

# La puerta esta EMPOTRADA en el muro: sin esto el muro veria un hueco y se
# rematarian los dos lados, como si la pared se cortara ahi
CONTINUAN = {'M': 'P'}

OBJETOS = {
    'Z': 'assets/tiles/tile_antorcha.png',
    'O': 'assets/tiles/tile_barril.png',
    'J': 'assets/tiles/tile_tinaja.png',
    'P': 'assets/tiles/puerta_muro.png',
}

SOLIDOS = {'M', 'O', 'J'}

JUGADOR_INICIO = (11, 9)
MUSICA = 'mazmorra.wav'
ENEMIGO = 'sombra'
OBJETIVO = 5

# El jefe del nivel. Se le vence ademas de despejar las sombras.
# La dificultad elegida multiplica su vida y sus puntos.
JEFE = {
    'nombre': 'La Bruja Misteriosa',
    'tipo': 'bruja',
    'x': 12, 'y': 2,          # donde aparece, en tiles
    'vida': 10,
    'velocidad': 68,
    'dano': 1,
    'puntos': 4000,
}

SALIDAS = {
    (11, 10): ('pueblo', 7, 20),
}

ES_FINAL = True
