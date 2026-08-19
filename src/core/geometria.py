"""
Calculos de cajas o hitboxes que usan varias partes del juego

Todo personaje jugador, NPC, enemigo colisiona solo con sus PIES, no con el
sprite entero
"""

import pygame

from config import settings as ajustes


#region Anclaje
# Donde se pega la caja dentro de su celda. Se escribe con palabras, no con
# numeros, el nivel se lee (0.9, 0.4, 'centro')
VERTICALES = ('arriba', 'centro', 'abajo')
HORIZONTALES = ('izquierda', 'centro', 'derecha')
ANCLAJE_POR_DEFECTO = 'abajo'


def descomponer_anclaje(anclaje):
    """
    'abajo-derecha' -> ('abajo', 'derecha')

    Se puede escribir un solo eje y el otro toma su valor natural ejemplos:

        'abajo'            -> ('abajo', 'centro')     el de default
        'centro'           -> ('centro', 'centro')
        'izquierda'        -> ('abajo', 'izquierda')
        'arriba-derecha'   -> ('arriba', 'derecha')
    """
    vertical = horizontal = None
    hay_centro = False
    for pieza in str(anclaje).lower().replace('_', '-').split('-'):
        pieza = pieza.strip()
        if not pieza:
            continue
        if pieza == 'centro':
            hay_centro = True
        elif pieza in VERTICALES:
            vertical = pieza
        elif pieza in HORIZONTALES:
            horizontal = pieza
        else:
            raise ValueError(
                f'Anclaje desconocido: {anclaje!r}. '
                f'Se arma con {list(VERTICALES)} y {list(HORIZONTALES)}, '
                'por ejemplo "abajo", "centro" o "arriba-izquierda"'
            )
    if hay_centro:
        # 'centro' se aplica al eje o ejes que no se hayan nombrado
        vertical = vertical or 'centro'
        horizontal = horizontal or 'centro'
    return vertical or 'abajo', horizontal or 'centro'
#endregion


def caja_base(x, y, ancho_celda, alto_celda, prop_ancho, prop_alto,
              margen=0, anclaje=ANCLAJE_POR_DEFECTO):
    """
    Rectangulo pegado a una parte de la celda, del tamano que se le pida.

    Es la unica forma de colisionar que hay en el juego: los personajes chocan
    por los pies y los objetos por la parte que de verdad toca el suelo. Un
    arbol de 64 px no estorba entero, estorba por el tronco.

    Las proporciones pueden pasar de 1.0 cuando el objeto es mas ancho que su
    celda, como una banca o una carreta. "margen" despega la caja del borde.
    """
    vertical, horizontal = descomponer_anclaje(anclaje)
    ancho = max(1, int(ancho_celda * prop_ancho))
    alto = max(1, int(alto_celda * prop_alto))

    if horizontal == 'izquierda':
        izq = margen
    elif horizontal == 'derecha':
        izq = ancho_celda - ancho - margen
    else:
        izq = (ancho_celda - ancho) // 2

    if vertical == 'arriba':
        arriba = margen
    elif vertical == 'centro':
        arriba = (alto_celda - alto) // 2
    else:
        arriba = alto_celda - alto - margen

    return pygame.Rect(int(x) + izq, int(y) + arriba, ancho, alto)


def caja_pies(x, y, lado, prop_ancho=None, prop_alto=None):
    #Caja en la base de un sprite cuadrado ubicado en (x, y)
    #"prop_ancho" y "prop_alto" son proporciones del sprite. Si no se pasan, se
    #usan las del jugador que estan en settings
    prop_ancho = ajustes.HITBOX_ANCHO if prop_ancho is None else prop_ancho
    prop_alto = ajustes.HITBOX_ALTO if prop_alto is None else prop_alto
    # El margen de 2 px despega la caja del borde del sprite
    return caja_base(x, y, lado, lado, prop_ancho, prop_alto, margen=2)


def caja_celda(col, fil, prop_ancho=1.0, prop_alto=1.0,
               anclaje=ANCLAJE_POR_DEFECTO):
    #Lo mismo, pero para una casilla del mapa dada en tiles
    return caja_base(col * ajustes.TILE_W, fil * ajustes.TILE_H,
                     ajustes.TILE_W, ajustes.TILE_H, prop_ancho, prop_alto,
                     anclaje=anclaje)


def caja_pies_jugador(x, y):
    return caja_pies(x, y, ajustes.JUG_W)


def caja_pies_enemigo(x, y):
    return caja_pies(x, y, ajustes.ENEMIGO_LADO,
                     ajustes.ENEMIGO_HITBOX_ANCHO,
                     ajustes.ENEMIGO_HITBOX_ALTO)


def caja_delante(x, y, lado, direccion, largo, ancho):
    #Rectangulo proyectado hacia donde mira un personaje
    cx = x + lado // 2
    cy = y + lado // 2
    if direccion == 'espalda':
        return pygame.Rect(cx - ancho // 2, cy - largo, ancho, largo)
    if direccion == 'frente':
        return pygame.Rect(cx - ancho // 2, cy, ancho, largo)
    if direccion == 'izquierda':
        return pygame.Rect(cx - largo, cy - ancho // 2, largo, ancho)
    return pygame.Rect(cx, cy - ancho // 2, largo, ancho)
