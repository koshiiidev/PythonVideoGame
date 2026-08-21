"""
Nivel: el pueblo

Este archivo es SOLO datos. Nada de logica: el cargador de niveles lo lee y la
escena de juego lo dibuja.

Leyenda del mapa
    .  pasto (el fondo por defecto)
    #  camino de piedra    autotileado
    ~  agua                autotileado
    B  tierra de la orilla autotileado
    V  cerca de madera     autotileado
    M  muro de piedra      autotileado
    A a q p                arboles comun, frutal, seco y palmera
    T  tronco caido        R  piedra        C  cafetal
    O  barril              J  tinaja
    1 2 3 4  casas del pueblo      5  la casona, es la unica en la que se entra
    K  chinamo   Z  pozo   Y  carreta   N  banca   F  farol
    P  puerta (no bloquea: es la salida)

Ademas de MAPA hay una capa DECOR con lo que se para encima del suelo.
"""

TITULO = 'Pueblo del Valle'

MAPA = [
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "A~~~~~~~~~~~~~~~~~~~~~~~~~~~~A",
    "A~~~~~~~~~~~~~~~~~~~~~~~~~~~~A",
    "ABBBBBBBBBBBBBBBBBBBBBBBBBBBBA",
    "A..A.p..p.A.p.##.p.A.p..p.A..A",
    "A.VVVVVVVVV...##....VVVVVVVV.A",
    "A.V.......Va..##..a.V......V.A",
    "A.V.1...2.V.R.##.R..V.3...4V.A",
    "A.V.......V...##....V......V.A",
    "A.VK..N...V########.VJ...Y.V.A",
    "A.VVV.VVVVV#F####F#.VVV.VVVV.A",
    "A.A.T.....q########......T.A.A",
    "A.##########################.A",
    "A.##########################.A",
    "A..........########..........A",
    "A.CCCCC....#FN##NF#a.......R.A",
    "A.CCCCC..a.########.MMMMMMM..A",
    "A.CC.CC...a...##...RM.....Mq.A",
    "A.CCCCC..R....##.q..M.O..OM..A",
    "A.....5....AT.##.T..MMM.MMM..A",
    "A.R...P#############.........A",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
]

# ----------------------------------------------------------------------------
# CAPA DE ENCIMA (opcional)
# ----------------------------------------------------------------------------
# MAPA es el suelo y lo que ocupa la casilla entera. DECOR es lo que se PARA
# sobre ese suelo. El hueco es el ESPACIO ' ', no el punto.
#
# Son dos capas porque una casilla guarda una sola letra. Con una sola capa,
# poner un barril en el camino borraba el camino y quedaba pasto debajo. Aca
# el camino se dibuja primero y el barril encima.
#
# Usa las mismas tablas que MAPA: OBJETOS para el sprite, SOLIDOS para saber si
# estorba, PROFUNDIDAD para pasarle por detras. Lo unico que NO va aca son los
# terrenos autotileados ni los objetos con HUELLA de varias casillas.
DECOR = [
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "     O   J       a    O  R    ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
    "                              ",
]

# Terrenos que se acomodan solos segun sus vecinos: caracter -> nombre del set de 16 tiles.
TERRENOS = {
    '#': 'camino',
    '~': 'agua',
    'B': 'tierra',
    'V': 'cerca',
    'M': 'muro',
}

# Objetos con sprite propio: caracter -> ruta de la imagen
OBJETOS = {
    'A': 'assets/tiles/arboles/arbol_1.png',
    'a': 'assets/tiles/arboles/arbol_frutal.png',
    'q': 'assets/tiles/arboles/arbol_seco.png',
    'p': 'assets/tiles/arboles/palmera_1.png',
    'T': 'assets/tiles/tile_tronco1.png',
    'P': 'assets/tiles/puerta_sola.png',
    'C': 'assets/tiles/tile_cafetal.png',
    'R': 'assets/tiles/tile_roca.png',
    'O': 'assets/tiles/tile_barril.png',
    'J': 'assets/tiles/tile_tinaja.png',
    # Construcciones, algunos ocupan varios tiles, ver ALTOS y HUELLAS
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

# Lo que no deja pasar. La puerta P queda fuera a proposito
SOLIDOS = {'~', 'V', 'M', 'A', 'a', 'q', 'p', 'T', 'C', 'R', 'O', 'J',
           '1', '2', '3', '4', '5', 'K', 'Z', 'Y', 'N', 'F'}

# ----------------------------------------------------------------------------
# LAS CUATRO TABLAS DE LOS OBJETOS
# ----------------------------------------------------------------------------
# Cada una responde UNA pregunta distinta sobre el mismo caracter:
#
#   ALTOS        de que TAMANO se dibuja        -> ancho en tiles
#   HUELLAS      cuantas CASILLAS ocupa         -> (ancho, alto) en tiles
#   PROFUNDIDAD  si el jugador puede pasarle POR DETRAS
#   COLISIONES   la CAJA que estorba dentro de la casilla  (esta en settings.py)
#
# El "hitbox" que se ve con la tecla G es COLISIONES, y son proporciones del
# tile, no tiles. La tabla comun esta en config/settings.py; si un nivel quiere
# otra medida para una letra, declara aqui su propio COLISIONES y pisa la comun
# ----------------------------------------------------------------------------

# COMO SE DIBUJA: caracter -> cuantos TILES de ancho ocupa la imagen
# El alto sale de la proporcion del PNG, asi una casa alta no se aplasta.
# Todo lo que aparezca aqui se ordena por profundidad automaticamente, porque
# se desborda de su casilla y taparia mal al jugador
ALTOS = {
    '1': 3.0, '2': 3.0, '3': 3.0, '4': 3.0, #Casas
    'A': 1.3,      #Arbol
    '5': 3.3,      # la casona
    'K': 1.5,      # chinamo
    'Z': 1.6,      # pozo
    'Y': 1.5,      # carreta
    'N': 1.5,      # banca
    'F': 0.5,      # farol de hierro
}

# CUANTO BLOQUEA: caracter -> (ancho, alto) en tiles.
# Es otra cosa que ALTOS. Una casa se DIBUJA de tres tiles de ancho y casi tres
# de alto, pero solo hace falta que BLOQUEE su planta, no el techo. Sin esto
# una casa de tres tiles taparia el paso solo en la casilla de su letra y se
# podria caminar por encima de la pared
HUELLAS = {
    '1': (3, 2), '2': (3, 2), '3': (3, 2), '4': (3, 2),
    '5': (3, 3),
}

# SE ORDENA POR PROFUNDIDAD: objetos de UN tile que igual se dibujan junto con
# los personajes, segun la Y de su base. Sirve para pasar por detras de un
# arbol. Los de ALTOS ya entran solos, no hace falta
# repetirlos aca
PROFUNDIDAD = {'A', 'a', 'q', 'p', 'R', 'J', 'O', 'C'}

# ----------------------------------------------------------------------------
# COSAS QUE NO ENTRAN EN EL ARRAY DEL MAPA
# ----------------------------------------------------------------------------
# El array guarda una letra por celda y la posicion se deduce de donde esta esa
# letra. Todo lo que no cumpla eso va aqui con la coordenada escrita a mano en
# tiles (columna, fila). Las coordenadas se ven en pantalla con la tecla G

# Donde arranca el jugador. None = centro del mapa
JUGADOR_INICIO = (14, 14)

MUSICA = 'pueblo.wav'

# Sombras que hay que disipar para que la niebla deje pasar. Hasta lograrlo las SALIDAS no responden
OBJETIVO = 10

NPCS = [
    {'sprite': 'npc_F_1.png', 'x': 3,  'y': 11, 'solido': True},
    {'sprite': 'npc_F_2.png', 'x': 7,  'y': 11, 'solido': True},
    {'sprite': 'npc_F_3.png', 'x': 13, 'y': 11, 'solido': True},
    {'sprite': 'npc_F_4.png', 'x': 22, 'y': 14, 'solido': True},
    #{'sprite': 'npc_F_5.png', 'x': 5,  'y': 9,  'solido': False},  # deja pasar
    {'sprite': 'npc_F_6.png', 'x': 24, 'y': 11, 'solido': True},
    {'sprite': 'npc_F_7.png', 'x': 16, 'y': 17, 'solido': True},
]

# ----------------------------------------------------------------------------
# SALIDAS: (columna, fila) que pisa el jugador -> (nivel, columna, fila) destino
# ----------------------------------------------------------------------------
# El destino es donde aparece en el otro nivel. Ojo de no dejarlo encima de otra
# salida, porque entraria en bucle
SALIDAS = {
    (6, 20): ('casa', 11, 8),   # la puerta de la casona
}
