# -*- coding: utf-8 -*-
"""
Nivel: la mazmorra bajo el pueblo.

Provisional, para probar los objetos nuevos

Leyenda
    M  muro de piedra oscura
    Z  antorcha
    O  barril
    J  tinaja
    P  puerta
"""

TITULO = 'Mazmorra'

MAPA = [
    "MMMMMMMMMMMMMMMMMMMMMMMMM",
    "M.......................M",
    "M.Z.........Z...........M",
    "M.......................M",
    "M...O......J............M",
    "M.......................M",
    "M.Z.....................M",
    "M.......................M",
    "M.......................M",
    "MMMMMMMMMMMPMMMMMMMMMMMMM",
]

TERRENOS = {}

# sobre piedra y no sobre pasto
SUELO = 'assets/tiles/tile_muro_mazmorra.png'

OBJETOS = {
    'M': 'assets/tiles/tile_pared.png',
    'Z': 'assets/tiles/tile_antorcha.png',
    'O': 'assets/tiles/tile_barril.png',
    'J': 'assets/tiles/tile_tinaja.png',
    'P': 'assets/tiles/tile_puerta.png',
}

SOLIDOS = {'M', 'O', 'J'}

JUGADOR_INICIO = (7, 7)
MUSICA = 'mazmorra.ogg'
ENEMIGO = 'sombra'
OBJETIVO = 5

# El jefe del nivel. Se le vence ademas de despejar las sombras.
# La dificultad elegida multiplica su vida y sus puntos.
JEFE = {
    'nombre': 'La Bruja Misteriosa',
    'tipo': 'bruja',
    'x': 7, 'y': 2,          # donde aparece, en tiles
    'vida': 10,
    'velocidad': 68,
    'dano': 1,
    'puntos': 4000,
}

SALIDAS = {
    (12, 10): ('pueblo', 12, 6),
}

ES_FINAL = True