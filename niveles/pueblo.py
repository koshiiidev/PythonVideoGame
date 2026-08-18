"""
Nivel: el pueblo

Este archivo es solo datos de configuración. La lógica está en src/core/niveles.py

Leyenda
    .  pasto
    #  camino de piedra   (autotileado)
    ~  agua               (autotileado)
    B  tierra / barro     (autotileado)
    M  pared              (sprite unico)
    A  arbol              (sprite unico, se dibuja con y-sort)
    T  tronco             (sprite unico)
    P  puerta             (sprite unico, no bloquea)
"""

TITULO = 'Pueblo'

MAPA = [
    "AAAAAAAAAAAAAAAAAAAAAAAAA",
    "A.......A...............A",
    "A.#####.A.MMMMM.........A",
    "A.#...#.A.M...M.~~~~~~..A",
    "A.#.T.#.A.M...M.~....~..A",
    "A.###.#...MMPMM.~....~..A",
    "A...#.#############..~..A",
    "AAA.#.............#..~..A",
    "A...###########.A.#..~..A",
    "A.A...........#.A.#..~..A",
    "A.AAAAA.......#####..~..A",
    "A.....A.MMMMM........~..A",
    "A.....A.M...M.~~~~~~~~..A",
    "A.######M...M.~.........A",
    "A.#.....MMMMM.~...AAAA..A",
    "A.#...........~...A..A..A",
    "A.#################..A..A",
    "A....................A..A",
    "AAAAAAAAAAAAAAAAAAAAAAAAA",
]

# Terrenos que se auto ajustan: caracter -> carpeta del tileset
TERRENOS = {'#': 'camino', '~': 'agua', 'B': 'tierra'}

# Objetos con un solo sprite: caracter -> ruta
OBJETOS = {
    'M': 'assets/tiles/tile_pared.png',
    'A': 'assets/tiles/tile_arbol.png',
    'T': 'assets/tiles/tile_tronco1.png',
    'P': 'assets/tiles/tile_puerta.png',
}

# Lo que bloquea el paso
SOLIDOS = {'M', 'A', 'T', '~'}

# ----------------------------------------------------------------------------
# COSAS QUE NO ENTRAN EN EL ARRAY DEL MAPA
# ----------------------------------------------------------------------------
# El array solo puede guardar una letra por celda, y la posicion se deduce de
# donde esta esa letra en el array del mapa. Todo lo que no cumpla eso (porque ocupa varios tiles,
# porque no esta alineado a la rejilla, o porque tiene estado propio) va aqui 
# con la coordenada escrita a mano en tiles (columna, fila) eso se puede ver en el modo depuracion tocanco la letra G

# Donde arranca el jugador. None = centro del mapa
JUGADOR_INICIO = None

# Musica de fondo del nivel. None = sin musica
MUSICA = 'pueblo.ogg' # este aun no existe

NPCS = [
    {'sprite': 'npc_F_1.png', 'x': 4,  'y': 2,  'solido': True},
    {'sprite': 'npc_F_2.png', 'x': 5,  'y': 2,  'solido': True},
    {'sprite': 'npc_F_3.png', 'x': 11, 'y': 4,  'solido': True},
    {'sprite': 'npc_F_4.png', 'x': 18, 'y': 4,  'solido': True},
    {'sprite': 'npc_F_5.png', 'x': 2,  'y': 8,  'solido': False},  # surfista, deja pasar
    {'sprite': 'npc_F_6.png', 'x': 10, 'y': 14, 'solido': True},
    {'sprite': 'npc_F_7.png', 'x': 16, 'y': 11, 'solido': True},
]

# ----------------------------------------------------------------------------
# SALIDAS: columna y fila que pisa el jugador y manda a (nivel, columna, fila) destino
# ----------------------------------------------------------------------------
# El destino es donde aparece en el otro nivel. Revisar que no caiga en una salida porque entra en bucle
SALIDAS = {
    (12, 5): ('casa', 4, 5),    # la puerta en la pared sur del cuarto
}
