"""
constantes del juego, las rutas son relativas a la raiz
"""

#region Ventana
ANCHO, ALTO = 800, 600
TITULO = "Cholito - La leyenda del valle"
FPS = 60
#endregion

#region Pasto
# Cada cuanto una celda de pasto usa una variante en vez del tile base.
# 0.0 = siempre el mismo. Sirve para que el zacate no se vea como un patron
# repetido. Los niveles que declaran su propio SUELO no se ven afectados.
PROB_VARIANTE_PASTO = 0.35
#endregion

#region Rejilla y sprites
TILE_W, TILE_H = 64, 64
TILE_ORIG_W, TILE_ORIG_H = 100, 100   # tamaño algunos spritesheets que toca escalar
JUG_W, JUG_H = 64, 64
ARBOL_ESCALA = 1.5                    # el árbol se dibuja más grande para que sobresalga un poco del tile
ARBOL_W = int(TILE_W * ARBOL_ESCALA)
ARBOL_H = int(TILE_H * ARBOL_ESCALA)
FPS_OBJETO = 7                        # ritmo de los objetos animados
#endregion

#region Jugador
VELOCIDAD_JUGADOR = 180               # píxeles por segundo
FRAMES_ANIM = 5                       # cuadros por spritesheet
FPS_ANIM = 6                          # cuadros por segundo al caminar
FPS_ATAQUE = 13                       # cuadros por segundo al atacar
HITBOX_ANCHO = 0.5                    # proporción del sprite (solo los pies para los npc y jugador)
HITBOX_ALTO = 0.2
#endregion

#region Depuracion
# Con esto en False no se dibujan hitboxes, no aparece la barra de info y la
# tecla G para mostrar la rejilla deja de funcionar.

MOSTRAR_DEPURACION = False

#endregion

#region Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (120, 120, 120)
COLOR_REJILLA = (220, 220, 220)
COLOR_FUERA_MAPA = (18, 20, 16)       # relleno cuando el mapa no llena la pantalla
HITBOX_JUGADOR = (255, 0, 0)
HITBOX_NPC = (0, 200, 0)
HITBOX_TILE = (0, 100, 200)
MENU_FONDO = (24, 28, 22)
MENU_TEXTO = (232, 232, 216)
MENU_RESALTE = (186, 211, 98)
#endregion

#region Rutas
DIR_TERRENO = 'assets/tiles/terreno'
DIR_JUGADOR = 'assets/characters/player'
DIR_NPC = 'assets/characters/npc'
DIR_TILES = 'assets/tiles'
DIR_ICONOS = 'assets/ui/iconos'
DIR_RETRATOS = 'assets/ui/retratos'
DIR_MUSICA = 'assets/audio/musica'
DIR_SFX = 'assets/audio/sfx'
PAQUETE_NIVELES = 'niveles'
#endregion

#region Partida
DIFICULTADES = {
    'Principiante': {'enemigos': 5, 'velocidad': 60,  'dano': 1, 'multiplicador': 1.0},
    'Normal':       {'enemigos': 10, 'velocidad': 85,  'dano': 1, 'multiplicador': 1.5},
    'Leyenda':      {'enemigos': 20, 'velocidad': 115, 'dano': 1, 'multiplicador': 2.5},
}
DIFICULTAD_POR_DEFECTO = 'Normal'

VIDAS_OPCIONES = (1, 3, 5)
VIDAS_POR_DEFECTO = 3

# Iconos que puede elegir cada jugador
# Retratos de Cholito. Es siempre el mismo personaje la expresion es la que cambia
ICONOS_JUGADOR = ('cholito_1.png', 'cholito_2.png', 'cholito_3.png',
                  'cholito_4.png', 'cholito_5.png', 'cholito_6.png')

LARGO_MAX_NOMBRE = 12
NOMBRE_POR_DEFECTO = 'Cholito'

# Puntos
PUNTOS_POR_ENEMIGO = 100
ENEMIGOS_PARA_BONO = 10
PUNTOS_BONO = 500
VELOCIDAD_POR_BONO = 12       # los enemigos se aceleran con cada bono
#endregion

#region Combate y enemigos
ENEMIGO_LADO = 48
CUADROS_ENEMIGO = 4
FPS_ENEMIGO = 6
ENEMIGO_HITBOX_ANCHO = 0.55   # proporciones de su caja de pies
ENEMIGO_HITBOX_ALTO = 0.35
DIR_ENEMIGOS = 'assets/characters/enemigos'

# Catalogo de criaturas. Cada una declara su tamano en pantalla y sus hojas/spritesheets.
# 'reposo' es obligatoria; 'dano' es opcional y si falta se usa el destello
ENEMIGOS = {
    'sombra': {
        'lado': 48, 'fps': 6, 'pingpong': False,
        'sprite': {'reposo': 'sombra.png'},
    },
    'segua': {
        'lado': 48, 'fps': 7, 'pingpong': False,
        'sprite': {'reposo': 'segua.png'},
    },
    'cadejos': {
        'lado': 48, 'fps': 8, 'pingpong': False,
        'sprite': {'reposo': 'cadejos.png'},
    },
    'bruja': {
        'lado': 128, 'fps': 5, 'pingpong': True,
        'hitbox_ancho': 0.42, 'hitbox_alto': 0.16,
        'sprite': {'reposo': 'bruja_F_sp.png', 'dano': 'bruja_F_dano.png'},
        'fps_dano': 14,
    },
}
ENEMIGO_POR_DEFECTO = 'sombra'

DISTANCIA_VISION = 220        # a que distancia el enemigo empieza a perseguir
DISTANCIA_APARICION = 260     # no aparecen mas cerca que esto del jugador
SEPARACION_ENEMIGOS = 110     # ni mas cerca que esto entre ellos
ALCANCE_ATAQUE = 46           # largo del machetazo en pixeles
ANCHO_ATAQUE = 46             # ancho del machetazo
# Al recibir un machetazo el enemigo sale despedido y queda unos instantes aturdido
RETROCESO_VELOCIDAD = 340     # que tan fuerte sale despedido
RETROCESO_S = 0.14            # cuanto dura el empuje
ATURDIMIENTO_S = 0.34         # cuanto queda quieto despues del empuje

INVULNERABLE_S = 1.2          # tiempo sin recibir daño tras un golpe
PARPADEO_HZ = 8               # velocidad del parpadeo mientras es invulnerable
#endregion

#region hitboxes
# Igual que los personajes chocan solo con los pies, los objetos chocan solo con
# la parte que de verdad toca el suelo. Un arbol no estorba con las hojas,
# estorba con el tronco.
#
#   caracter -> (ancho, alto)             como PROPORCION del tile
#   caracter -> (ancho, alto, anclaje)    si hay que pegarla a otro lado
#
# (1.0, 1.0) es la casilla entera. Se puede pasar de 1.0 cuando el objeto se
# dibuja mas ancho que su casilla, como la banca o la carreta.
#
# EL ANCLAJE dice a que parte de la casilla se pega la caja. Si no se escribe,
# es 'abajo' apoyada en el piso y centrada a lo ancho
# Se arma con estas palabras, solas o unidas con guion
#
#       arriba   centro   abajo          (eje vertical)
#       izquierda  centro  derecha       (eje horizontal)
#
#   'abajo'            apoyada abajo, centrada a lo ancho
#   'centro'           en el medio de la casilla, los dos ejes
#   'izquierda'        pegada a la izquierda, apoyada abajo
#   'arriba-derecha'   en la esquina de arriba a la derecha
#
# Esta tabla es la convencion de letras del proyecto y sirve de valor por
# defecto cada nivel puede reescribir lo que quiera con su propio COLISIONES.
COLISION_POR_DEFECTO = (1.0, 1.0)   # lo que no aparezca aqui bloquea entero

# Cosas entre las que SE PUEDE pasar a proposito. Una fila de cosas solidas
# normalmente tiene que ser una barrera, y si entre dos vecinas cabe el jugador
# es un error de medidas. Pero hay excepciones queridas: por el cafetal se
# camina entre las hileras, como en un cafetal de verdad. Lo que este aqui no
# se reporta como hueco.
ATRAVESABLES = {'C'}
COLISIONES = {
    # Terreno
    '~': (0.70, 0.85, 'centro'),   # agua
    'M': (0.70, 0.85),             # muro
    'V': (0.70, 0.85),             # cerca: se apoya en la mitad de abajo del tile

    # Vegetacion
    'A': (0.55, 0.83),             # arbol comun
    'a': (0.45, 0.50, 'centro'),   # arbol frutal
    'q': (0.50, 0.45, 'centro'),   # arbol seco
    'p': (0.25, 0.50, 'centro'),   # palmera chiquita
    'C': (0.45, 0.55),             # cafetal
    'T': (0.90, 0.40, 'centro'),   # tronco caido
    'R': (0.90, 0.80),             # piedra

    # Cosas
    'O': (0.70, 0.50),   # barril
    'J': (0.45, 0.28),   # tinaja
    'N': (1.30, 0.40),   # banca, se dibuja mas ancha que su tile
    'F': (0.30, 0.35),   # farol
    'Z': (1.20, 0.55),   # pozo
    'K': (1.20, 0.50),   # chinamo
    'Y': (1.20, 0.45),   # carreta
}
#endregion

#region Archivos

ARCHIVO_ESTADISTICAS = 'datos/estadisticas.json'

#endregion

#region Niveles

NIVEL_INICIAL = 'pueblo'

#endregion

#region Audio
VOLUMEN_MUSICA = 0.5
VOLUMEN_SFX = 0.7
FADE_MUSICA_MS = 600
#endregion
