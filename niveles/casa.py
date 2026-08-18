"""
interior de la casa.

"""

TITULO = 'Casa'

MAPA = [
    "MMMMMMMMM",
    "MFFFFFFFM",
    "MFFFFFFFM",
    "MFFFFFFFM",
    "MFFFFFFFM",
    "MFFFFFFFM",
    "MMMMPMMMM",
]

TERRENOS = {'#': 'camino', '~': 'agua', 'B': 'tierra'}

OBJETOS = {
    'M': 'assets/tiles/tile_pared.png',
    'T': 'assets/tiles/tile_tronco1.png',
    'P': 'assets/tiles/tile_puerta.png',
    'F': 'assets/tiles/tile_piso.png',      # piso de madera
}

SOLIDOS = {'M', '~'}

JUGADOR_INICIO = (4, 5)
MUSICA = 'casa.ogg'

NPCS = [
    {'sprite': 'npc_F_6.png', 'x': 2, 'y': 2, 'solido': True},
]

# la puerta de abajo devuelve al pueblo
SALIDAS = {
    (4, 6): ('pueblo', 12, 6),
}
