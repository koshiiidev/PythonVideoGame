"""
Revision de un nivel: caza los errores tipicos de dibujar un mapa a mano.

Un mapa se escribe como texto, asi que los errores son de escritura: una fila
a la que le falta una letra, una salida sobre una piedra, un NPC metido en una
pared, una tabla que nombra una letra que no existe. Todo eso se puede saber
SIN abrir el juego, y es mucho mas rapido que descubrirlo jugando.

Aca viven las revisiones que solo necesitan los DATOS del nivel. Las que
necesitan el juego andando (que la bruja alcance al jugador, que el visor abra)
se quedan en pruebas_niveles.py, que es quien tiene pygame en marcha.

Uso:

    from src.core import revision_niveles
    for problema in revision_niveles.problemas(nivel):
        print(problema)

Devuelve una lista de textos. Lista vacia = el nivel esta bien.
"""

from collections import deque

from config import settings as ajustes
from src.core import geometria

# En la capa DECOR el hueco es el espacio, no el punto
VACIO_DECOR = ' '


#region Recorrido
def alcanzables(nivel, desde):
    """
    Casillas a las que se puede llegar caminando desde `desde`.

    Es una inundacion por las celdas libres. Sirve para saber si una salida
    quedo encerrada detras de una pared, que a ojo no se nota.
    """
    vistos = set()
    cola = deque([desde])
    while cola:
        col, fil = cola.popleft()
        if (col, fil) in vistos:
            continue
        if not (0 <= col < nivel.cols and 0 <= fil < nivel.filas):
            continue
        if nivel.es_solido(col, fil):
            continue
        vistos.add((col, fil))
        cola.extend([(col + 1, fil), (col - 1, fil),
                     (col, fil + 1), (col, fil - 1)])
    return vistos
#endregion


#region Revisiones sueltas
def _forma(nivel):
    #Todas las filas del MAPA tienen que medir lo mismo
    largos = set(len(f) for f in nivel.mapa)
    if len(largos) > 1:
        yield 'MAPA tiene filas de distinto largo: %s' % sorted(largos)


def _caracteres(nivel):
    #Toda letra usada tiene que estar declarada en algun lado
    conocidos = set(nivel.terrenos) | set(nivel.objetos) | {'.'}
    for fil in range(nivel.filas):
        for col in range(len(nivel.mapa[fil])):
            letra = nivel.mapa[fil][col]
            if letra not in conocidos:
                yield ('MAPA (%d,%d): la letra %r no esta en TERRENOS ni en '
                       'OBJETOS' % (col, fil, letra))


def _arranque_y_salidas(nivel):
    #Que el jugador pueda empezar, y que pueda LLEGAR a cada salida
    inicio = nivel.inicio or (nivel.cols // 2, nivel.filas // 2)
    if nivel.es_solido(*inicio):
        yield 'JUGADOR_INICIO %s: sobre algo solido' % (inicio,)
        return          # sin punto de partida no se puede inundar nada

    libres = alcanzables(nivel, inicio)
    for celda, destino in nivel.salidas.items():
        if celda not in libres:
            yield ('SALIDA %s: no se puede llegar caminando hasta ahi'
                   % (celda,))
        # El destino esta en OTRO nivel, asi que hay que cargarlo
        from src.core import cargador_niveles
        try:
            otro = cargador_niveles.cargar(destino[0])
        except Exception as error:
            yield ('SALIDA %s: el nivel destino %r no se pudo cargar (%s)'
                   % (celda, destino[0], error))
            continue
        if otro.es_solido(destino[1], destino[2]):
            yield ('SALIDA %s: deja al jugador dentro de un solido de %s %s'
                   % (celda, destino[0], destino[1:]))
        elif otro.salida_en(destino[1], destino[2]) is not None:
            yield ('SALIDA %s: cae encima de otra salida en %s, el jugador '
                   'entraria en bucle' % (celda, destino[0]))

    if nivel.jefe:
        sitio = (nivel.jefe.get('x'), nivel.jefe.get('y'))
        if sitio not in libres:
            yield 'JEFE en %s: aparece donde el jugador no puede llegar' % (sitio,)


def _cajas(nivel):
    #Ninguna caja de colision puede salirse de su propia casilla
    alto = ajustes.TILE_H
    for fil in range(nivel.filas):
        for col in range(nivel.cols):
            if not nivel.es_solido(col, fil):
                continue
            caja = geometria.caja_celda(col, fil, *nivel.colision(col, fil))
            if caja.width <= 0 or caja.height <= 0:
                yield ('COLISIONES: la caja de %s queda vacia'
                       % _quien(nivel, col, fil))
            if not (fil * alto <= caja.top and caja.bottom <= (fil + 1) * alto):
                yield ('COLISIONES: la caja de %s en (%d,%d) se sale de su '
                       'casilla' % (_quien(nivel, col, fil), col, fil))


def _dueno(nivel, col, fil):
    #La letra del objeto que ocupa esa casilla: la suya, o la del objeto grande
    #cuya huella le cae encima
    return nivel.bloqueados.get((col, fil)) or nivel.celda(col, fil)


def _quien(nivel, col, fil):
    #Como se nombra lo que estorba en esa casilla. Si es la huella de un objeto
    #grande se nombra el objeto, porque en el mapa ahi solo hay un punto
    dueno = nivel.bloqueados.get((col, fil))
    if dueno and dueno != nivel.celda(col, fil):
        return 'la huella de %r' % dueno
    return repr(nivel.celda(col, fil))


def _huecos(nivel):
    """
    Una fila de cosas solidas tiene que ser una BARRERA, no un colador.

    Al achicar las cajas para que se vieran naturales pueden quedar pasillos:
    si entre las cajas de dos vecinas cabe la caja de pies del jugador, se
    puede colar por ahi.

    Se comparan solo vecinas del MISMO objeto, porque una barrera es una fila
    de lo mismo: la arboleda del borde, una cerca, las hileras del cafetal. Que
    entre un estante y un barril quepa una persona no es un error, es una casa.

    OJO: esto avisa de CANDIDATOS, no de certezas. Solo mira el par de vecinas,
    no comprueba que se pueda llegar hasta el hueco, asi que si una tercera
    cosa solida tapa el paso da falsa alarma. Lo que se pasa a proposito, como
    el cafetal, se declara en ATRAVESABLES y no se reporta.
    """
    pies = geometria.caja_pies_jugador(0, 0)
    encontrados = {}
    for fil in range(nivel.filas):
        for col in range(nivel.cols):
            if not nivel.es_solido(col, fil):
                continue
            letra = _quien(nivel, col, fil)
            if nivel.celda(col, fil) in nivel.atravesables:
                continue
            caja = geometria.caja_celda(col, fil, *nivel.colision(col, fil))
            for dcol, dfil, eje, cabe in ((1, 0, 'horizontal', pies.width),
                                          (0, 1, 'vertical', pies.height)):
                vcol, vfil = col + dcol, fil + dfil
                if not (vcol < nivel.cols and vfil < nivel.filas):
                    continue
                if not nivel.es_solido(vcol, vfil):
                    continue
                # Solo cuentan las filas del MISMO objeto: dos cosas distintas
                # una al lado de la otra no son una barrera
                if _dueno(nivel, col, fil) != _dueno(nivel, vcol, vfil):
                    continue
                otra = geometria.caja_celda(vcol, vfil,
                                            *nivel.colision(vcol, vfil))
                hueco = (otra.left - caja.right if eje == 'horizontal'
                         else otra.top - caja.bottom)
                if hueco >= cabe:
                    clave = (letra, eje, hueco, cabe)
                    encontrados[clave] = encontrados.get(clave, 0) + 1

    # Se agrupa por letra y eje: si no, un borde de arboles escupe 50 lineas
    for (letra, eje, hueco, cabe), cuantos in sorted(encontrados.items()):
        yield ('COLISIONES: entre dos %s seguidos en %s cabe el jugador '
               '(hueco de %d px contra %d) en %d sitios. Si algo mas tapa el '
               'paso es falsa alarma; si se pasa a proposito, va en '
               'ATRAVESABLES' % (letra, eje, hueco, cabe, cuantos))


def _tablas(nivel):
    #Las tablas de objetos tienen que hablar de letras que existan en el mapa
    declaradas = set(nivel.objetos) | set(nivel.terrenos)
    propias = getattr(nivel.modulo, 'COLISIONES', {}) or {}
    for tabla, nombre in ((nivel.altos, 'ALTOS'),
                          (nivel.huellas, 'HUELLAS'),
                          (propias, 'COLISIONES')):
        for letra in tabla:
            if letra not in declaradas:
                yield ('%s declara %r y esa letra no esta en OBJETOS ni en '
                       'TERRENOS' % (nombre, letra))
    for letra in nivel.profundidad:
        if letra not in nivel.objetos:
            yield 'PROFUNDIDAD declara %r y no esta en OBJETOS' % letra


def _decor(nivel):
    """
    Revisa la capa de encima. Sus errores son propios: en DECOR el hueco es el
    ESPACIO, no el punto, y hay cosas que no pueden ir ahi.
    """
    # getattr: antes de que exista la capa DECOR este atributo no esta, y la
    # revision simplemente no aplica
    if getattr(nivel, 'decor', None) is None:
        return
    crudo = getattr(nivel.modulo, 'DECOR', []) or []
    if len(crudo) != nivel.filas:
        yield ('DECOR tiene %d filas y MAPA tiene %d'
               % (len(crudo), nivel.filas))

    for fil in range(nivel.filas):
        for col in range(nivel.cols):
            adorno = nivel.adorno(col, fil)
            if adorno == VACIO_DECOR:
                continue
            if adorno == '.':
                yield ('DECOR (%d,%d): aqui el hueco es el espacio " ", no el '
                       'punto' % (col, fil))
            elif adorno not in nivel.objetos:
                yield ('DECOR (%d,%d): la letra %r no esta en OBJETOS'
                       % (col, fil, adorno))
            elif adorno in nivel.terrenos:
                yield ('DECOR (%d,%d): %r es un TERRENO, y los terrenos van en '
                       'MAPA porque se autotilean con sus vecinos'
                       % (col, fil, adorno))
            elif adorno in nivel.huellas:
                yield ('DECOR (%d,%d): %r tiene HUELLA de varias casillas y eso '
                       'solo se calcula sobre MAPA' % (col, fil, adorno))
            elif (nivel.celda(col, fil) in nivel.solidos
                  and adorno in nivel.solidos):
                yield ('DECOR (%d,%d): %r es solido y el suelo %r tambien; se '
                       'tapan entre si' % (col, fil, adorno,
                                           nivel.celda(col, fil)))


def _npcs(nivel):
    #Un NPC dentro de una pared se ve mal y puede tapar un paso
    for npc in nivel.npcs:
        col, fil = npc.get('x', 0), npc.get('y', 0)
        if not (0 <= col < nivel.cols and 0 <= fil < nivel.filas):
            yield 'NPC %s en (%d,%d): fuera del mapa' % (npc.get('sprite'), col, fil)
        elif nivel.es_solido(col, fil):
            yield ('NPC %s en (%d,%d): encima de algo solido'
                   % (npc.get('sprite'), col, fil))
#endregion


REVISIONES = (_forma, _caracteres, _decor, _arranque_y_salidas, _cajas,
              _huecos, _tablas, _npcs)


def problemas(nivel):
    #Junta todo. Lista vacia = el nivel esta bien
    fallos = []
    for revision in REVISIONES:
        fallos.extend(revision(nivel))
    return fallos
