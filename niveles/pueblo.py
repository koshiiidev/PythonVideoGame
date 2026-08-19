"""
Nivel: el pueblo

Este archivo es solo datos de configuración del mapa

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
    "A..C.C..A..1...R...3....A",
    "A.#####.A.MMMMM....C.C..A",
    "A.#...#.A.M...M.~~~~~~..A",
    "A.#.T.#.A.M.J.M.~....~..A",
    "A.###.#...MMPMM.~....~..A",
    "A.RN#.#############..~..A",
    "AAA.#.............#..~..A",
    "A.K.###########.A.#..~..A",
    "A.A...........#.A.#..~..A",
    "A.AAAAA.......#####..~..A",
    "A.C.C.A.MMMMM..O..Z..~..A",
    "A..Y..A.M...M.~~~~~~~~..A",
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
    'A': 'assets/tiles/arboles/arbol_1.png',
    'T': 'assets/tiles/tile_tronco1.png',
    'P': 'assets/tiles/tile_puerta.png',
    'C': 'assets/tiles/tile_cafetal.png',
    'R': 'assets/tiles/tile_roca.png',
    'L': 'assets/tiles/tile_farol.png',
    'O': 'assets/tiles/tile_barril.png',
    'J': 'assets/tiles/tile_tinaja.png',
    # Construcciones: ocupan varios tiles, ver ALTOS
    '1': 'assets/tiles/casa1.png',
    '2': 'assets/tiles/casa2.png',
    '3': 'assets/tiles/casa3.png',
    '4': 'assets/tiles/casa4.png',
    '5': 'assets/tiles/casa5.png',
    'K': 'assets/tiles/chinamo.png',
    'Z': 'assets/tiles/pozo.png',
    'Y': 'assets/tiles/carreta.png',
    'N': 'assets/tiles/banca.png',
    'F': 'assets/tiles/farol.png',
}

# Lo que bloquea el paso
SOLIDOS = {'M', 'A', 'T', '~', 'C', 'R', 'L', 'O', 'J',
           '1', '2', '3', '4', '5', 'K', 'Z', 'Y', 'N', 'F'}

# Caracteres que se dibujan mas grandes que su tile y se ordenan por
# profundidad, para poder caminar por detras. Todo lo demas ocupa su casilla
# entera, asi se ve claro que bloquea.
# caracter -> cuantos TILES de ancho ocupa. El alto sale de la proporcion de
# la imagen, asi una casa alta no se aplasta. Se apoyan por la base, se
# desbordan hacia arriba y se ordenan por profundidad.
ALTOS = {
    '1': 3.0, '2': 3.0, '3': 3.0, '4': 3.0, '5': 4.0,
    'K': 2.0,      # chinamo
    'Z': 2.0,      # pozo
    'Y': 2.0,      # carreta
    'N': 1.6,      # banca
    'F': 1.0,      # farol de hierro
}

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
MUSICA = 'pueblo.ogg'

# Sombras que hay que disipar para que la niebla deje pasar. Hasta lograrlo,
# las SALIDAS no responden.
OBJETIVO = 6 # este aun no existe

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
