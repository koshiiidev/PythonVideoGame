"""
Cada enemigo se mueve solo: si el jugador esta cerca lo persigue, y si no
deambula. La escena le pasa la funcion para consultar si una posicion choca con el mapa

Cada uno lleva su propio tamaño y su propio Animador, el tamaño sale del catalogo en settings.py
"""

import math
import random
import pygame

from config import settings as ajustes
from src.core import geometria
from src.core.animacion import Animacion, Animador


def _ficha(tipo):
    # Los datos del catalogo
    return ajustes.ENEMIGOS.get(tipo) or ajustes.ENEMIGOS[ajustes.ENEMIGO_POR_DEFECTO]


def crear_animador(tipo):
    # Arma el Animador de un tipo de criatura leyendo el catalogo

    # Se llama una vez por enemigo, pero los sprites se comparten entre animadores
    ficha = _ficha(tipo)
    lado = ficha['lado']
    animaciones = {}
    for estado, archivo in ficha['sprite'].items():
        ruta = f"{ajustes.DIR_ENEMIGOS}/{archivo}"
        # El daño se reproduce una sola vez y mas rapido, el reposo va en bucle
        es_dano = (estado == 'dano')
        animaciones[estado] = Animacion(
            ruta, lado=lado,
            fps=ficha.get('fps_dano', 12) if es_dano else ficha.get('fps', 6),
            bucle=not es_dano,
            pingpong=ficha.get('pingpong', False) and not es_dano)
    return Animador(animaciones, estado='reposo')


class Enemigo(object):

    def __init__(self, x, y, tipo='sombra', velocidad=None, vida=1,
                 dano=1, puntos=None):
        #region Validaciones
        vida = int(vida)
        if vida < 1:
            raise ValueError('Un enemigo necesita al menos un punto de vida')
        #endregion

        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo
        self.velocidad = float(velocidad or ajustes.DIFICULTADES[
            ajustes.DIFICULTAD_POR_DEFECTO]['velocidad'])
        self.vida = vida
        self.vida_maxima = vida
        self.dano = int(dano)
        self.puntos = int(ajustes.PUNTOS_POR_ENEMIGO if puntos is None else puntos)

        #region Tamaño
        ficha = _ficha(tipo)
        self.lado = int(ficha['lado']) #Tamaño del enemigo que viene del catalogo en settings
        self.prop_ancho = ficha.get('hitbox_ancho', ajustes.ENEMIGO_HITBOX_ANCHO) #Tamaño de la caja de colisión
        self.prop_alto = ficha.get('hitbox_alto', ajustes.ENEMIGO_HITBOX_ALTO)
        self.animador = crear_animador(tipo)#Animador del enemigo
        #endregion

        #region Estado interno
        self.vivo = True
        self.t_retroceso = 0.0        # mientras dura sale despedido
        self.t_aturdido = 0.0         # despues queda quieto un instante
        self._empuje = (0.0, 0.0)
        self._t_rumbo = 0.0
        self._rumbo = (0.0, 0.0)
        self._rng = random.Random(int(x) * 31 + int(y) * 17)
        #endregion

    #region Medidas
    @property
    def rect(self):
        #Caja completa, para dibujar y para recibir golpes
        return pygame.Rect(int(self.x), int(self.y), self.lado, self.lado)

    @property
    def hitbox(self):
        #Solo la base igual que el jugador
        return self.caja_en(self.x, self.y)

    def caja_en(self, x, y):
        return geometria.caja_pies(x, y, self.lado, self.prop_ancho, self.prop_alto)

    @property
    def y_sort(self):
        return self.y + self.lado

    @property
    def imagen(self):
        return self.animador.imagen
    #endregion

    #region Movimiento
    def _elegir_rumbo(self): #elije una direccion aleatoria y el tiempo que durara
        angulo = self._rng.uniform(0, 2 * math.pi) #Angulo aleatorio
        self._rumbo = (math.cos(angulo), math.sin(angulo)) #Vector de direccion
        self._t_rumbo = self._rng.uniform(0.8, 2.2) #Tiempo que durara en esa direccion

    def actualizar(self, dt, objetivo, choca):
        #"objetivo" es el x, y del jugador. choca recibe un Rect y dice
        # si esa posicion es solida.
        if not self.vivo:
            return

        self._animar(dt)

        # Primero el empuje del golpe, despues el aturdimiento
        #mientras dure alguno de los dos el enemigo no persigue
        if self.t_retroceso > 0:
            self.t_retroceso -= dt
            self._mover(self._empuje, ajustes.RETROCESO_VELOCIDAD * dt, choca)
            return
        if self.t_aturdido > 0:
            self.t_aturdido -= dt
            return

        dx, dy = self._direccion(dt, objetivo) #Direccion del enemigo
        self._mover((dx, dy), self.velocidad * dt, choca) #Movimiento del enemigo
        self._mirar(dx, dy) #Orientacion del enemigo

    def _mover(self, direccion, paso, choca):
        dx, dy = direccion
        nueva_x = self.x + dx * paso
        if not choca(self.caja_en(nueva_x, self.y)): #revisa si choca en la posicion nueva
            self.x = nueva_x #Si no choca, se mueve a la nueva posicion

        nueva_y = self.y + dy * paso
        if not choca(self.caja_en(self.x, nueva_y)): #revisa si choca en la posicion nueva
            self.y = nueva_y #Si no choca, se mueve a la nueva posicion

    def _direccion(self, dt, objetivo): #si ve al jugador lo persigue si no deambula
        #Persigue si ve al jugador si no deambula
        if objetivo:
            ox, oy = objetivo #Posicion del jugador
            dx = ox - self.x #Diferencia entre jugador y enemigo en x
            dy = oy - self.y #Diferencia entre jugador y enemigo en y
            distancia = math.hypot(dx, dy) #Distancia entre jugador y enemigo, sacando la hipotenusa
            if 0 < distancia <= ajustes.DISTANCIA_VISION: #Si la distancia es menor o igual a la vision
                return dx / distancia, dy / distancia #Retorna la direccion del enemigo en modo tupla

        self._t_rumbo -= dt #Resta tiempo al rumbo
        if self._t_rumbo <= 0: #Si el tiempo del rumbo es menor a 0, o sea ya se termino el tiempo de ese rumbo
            self._elegir_rumbo() #Elige un nuevo rumbo y se lo asigna a _rumbo
        return self._rumbo #Retorna el rumbo

    def _mirar(self, dx, dy):
        #Gira hacia donde se desplaza. Si su sprite no tiene direcciones, el Animador lo ignora y no pasa nada
        if abs(dx) < 0.05 and abs(dy) < 0.05:
            return
        if abs(dy) >= abs(dx):
            self.animador.cambiar(direccion='frente' if dy > 0 else 'espalda')
        else:
            self.animador.cambiar(direccion='derecha' if dx > 0 else 'izquierda')

    def _animar(self, dt):
        self.animador.actualizar(dt)
        # El daño es de una sola pasada: al terminar se vuelve al reposo
        if self.animador.estado == 'dano' and self.animador.termino:
            self.animador.cambiar(estado='reposo')
    #endregion

    #region Combate
    def recibir_golpe(self, dano=1, desde=None):
        #Devuelve True si el golpe lo mato
        #"desde" es el (x, y) de quien golpeo y se usa para saber hacia donde sale despedido
        if not self.vivo:
            return False
        self.vida -= max(1, int(dano)) #Resta vida al enemigo
        if self.vida <= 0: #Si la vida es menor o igual a 0
            self.vivo = False #El enemigo muere
            return True

        # Sobrevivio? sale despedido y queda aturdido, para dar tiempo al siguiente machetazo
        self.empujar(desde)
        if self.animador.tiene('dano'): #Si tiene animacion de daño
            self.animador.cambiar(estado='dano', reiniciar=True) #Cambia a animacion de daño
        return False

    def empujar(self, desde=None):
        #Lo lanza en direccion contraria a "desde" y lo deja aturdido
        if desde:
            dx = self.x - desde[0]
            dy = self.y - desde[1]
            distancia = math.hypot(dx, dy)
            self._empuje = (dx / distancia, dy / distancia) if distancia else (0.0, 1.0)
        else:
            self._empuje = (0.0, 1.0)
        self.t_retroceso = ajustes.RETROCESO_S
        self.t_aturdido = ajustes.ATURDIMIENTO_S

    @property
    def golpeado(self):
        #Sirve para destellar mientras se recupera
        return self.t_retroceso > 0 or self.t_aturdido > 0

    @property
    def destella(self):
        #Si tiene animacion de daño propia no hace falta el destello por codigo
        return self.golpeado and not self.animador.tiene('dano')

    def toca(self, rect):
        return self.vivo and self.hitbox.colliderect(rect)
    #endregion

    def __repr__(self):
        return f'<Enemigo {self.tipo} ({self.x},{self.y}) vida={self.vida}/{self.vida_maxima} lado={self.lado}>'
