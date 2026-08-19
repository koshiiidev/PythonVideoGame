"""
Motor de animacion, compartido por jugador, NPC y enemigos.

   La cantidad de frames se deduce del tamaño de la imagen y el tamaño indicado de cada frame
   frame = ancho de la imagen // alto de la imagen
   Una hoja de 1024x256 son 4 frames, y una imagen suelta de 256x256 es 1, son ejemplos pueden ser otros tamaños
"""

import os
import pygame

#los enemigos que se repiten se carga una sola vez
_cache_frames = {}


def cortar(ruta, lado=None, lado_origen=None):
    """Corta un sprite horizontal y devuelve la lista de frames.

    "lado_origen" es el tamano del frame en el archivo. Si no se pasa, se
    asume que los frames son cuadrados y se toma el alto de la imagen.
    "lado" es el tamano final en pantalla. Si no se pasa, no se escala.
    """
    clave = (ruta, lado, lado_origen)
    if clave in _cache_frames: #si existe la clave
        return _cache_frames[clave]

    if not os.path.exists(ruta): #si no existe la ruta
        print('[animacion] no se encontro:', ruta)
        _cache_frames[clave] = []
        return []

    hoja = pygame.image.load(ruta).convert_alpha() #carga la imagen
    origen = lado_origen or hoja.get_height() #tamaño del frame en el archivo
    total = max(1, hoja.get_width() // origen) #numero de frames
    destino = lado or origen #tamaño final en pantalla

    if destino != origen:
        hoja = pygame.transform.scale(hoja, (total * destino, destino)) #escala la imagen

    frames = [hoja.subsurface((i * destino, 0, destino, destino))
               for i in range(total)] #divide la imagen en frames
    _cache_frames[clave] = frames #guarda la imagen
    return frames 


class Animacion(object):
    #Una secuencia de frames con su propio reloj

    def __init__(self, ruta, lado=None, fps=8, bucle=True, pingpong=False,
                 lado_origen=None):
        self.frames = cortar(ruta, lado, lado_origen) #obtiene los frames
        self.fps = max(1, int(fps)) #velocidad de la animacion
        self.bucle = bool(bucle) #si se repite la animacion

        #region Orden animacion
        # El ping-pong va y vuelve sin repetir los extremos: 0,1,2,3,2,1
        n = len(self.frames) #numero de frames
        if pingpong and n > 2: #si se repite y hay mas de 2 frames
            self.orden = list(range(n)) + list(range(n - 2, 0, -1)) #repite los frames
        else:
            self.orden = list(range(n)) 
        #endregion

        self.paso = 0 #indice del frame actual
        self._t = 0.0 #tiempo actual

    #region Reproduccion
    def reiniciar(self):
        self.paso = 0 #reinicia el frame actual
        self._t = 0.0 #reinicia el tiempo actual

    def actualizar(self, dt):
        if len(self.orden) <= 1:
            return #una sola imagen no hay nada que avanzar
        self._t += dt #incrementa el tiempo actual
        intervalo = 1.0 / self.fps #calcula el intervalo entre frames
        while self._t >= intervalo: #mientras el tiempo actual sea mayor al intervalo
            self._t -= intervalo #resta el intervalo al tiempo actual
            if self.paso + 1 < len(self.orden): #si el paso actual es menor al numero de frames
                self.paso += 1 #incrementa el paso actual
            elif self.bucle: #si se repite la animacion
                self.paso = 0 #reinicia el paso actual
            else:
                break

    @property
    def termino(self):
        #se usa para las animaciones que no son bucle
        return not self.bucle and self.paso >= len(self.orden) - 1

    @property
    def imagen(self):
        if not self.frames: #si no hay frames
            return None
        return self.frames[self.orden[self.paso]] #retorna el frame actual

    @property
    def lado(self): #tamaño del frame
        return self.frames[0].get_width() if self.frames else 0
    #endregion

    def clonar(self):
        #copia los frames y arranca su propio contador
        otra = Animacion.__new__(Animacion) #crea una nueva instancia
        otra.frames = self.frames
        otra.fps = self.fps
        otra.bucle = self.bucle
        otra.orden = self.orden
        otra.paso = 0
        otra._t = 0.0
        return otra


class Animador(object):
    """Coleccion de animaciones con un estado y una direccion activos

    "animaciones" es un diccionario donde cada valor puede ser:
      - una Animacion suelta, si ese estado no depende de la direccion
      - un diccionario {direccion: Animacion}

        Animador({
            'reposo': {'frente': Animacion(...), 'espalda': Animacion(...)},
            'dano':   Animacion(...),
        })
    """

    def __init__(self, animaciones, estado='reposo', direccion='frente'):
        if not animaciones:
            raise ValueError('El animador necesita al menos una animacion')
        self.animaciones = animaciones #diccionario con las animaciones
        self.estado = estado if estado in animaciones else list(animaciones)[0] #estado actual
        self.direccion = direccion #direccion actual

    #region Cambio de estado
    def cambiar(self, estado=None, direccion=None, reiniciar=False): 
        #cambia estado, direccion o ambos
        #Si ya estaba en ese estado no lo reinicia, salvo que se pida, si no se quedaria trabada en el primer cuadro
        cambio = False
        if estado is not None and estado != self.estado and estado in self.animaciones: #compara estado
            self.estado = estado
            cambio = True
        if direccion is not None and direccion != self.direccion: #compara direccion
            self.direccion = direccion
            cambio = True
        if cambio or reiniciar: #si hay cambio o se pide reiniciar
            actual = self.actual
            if actual:
                actual.reiniciar()
        return cambio

    def tiene(self, estado): #dice si tiene una animacion para ese estado
        return estado in self.animaciones
    #endregion

    #region Consultas
    @property
    def actual(self): 
        #retorna la animacion actual
        entrada = self.animaciones.get(self.estado) #obtiene la animacion actual
        if entrada is None:
            return None
        if isinstance(entrada, dict):
            # Si falta esa direccion se usa cualquiera, para no quedar sin dibujo
            return entrada.get(self.direccion) or next(iter(entrada.values()), None)
        return entrada

    @property
    def imagen(self): 
        #retorna la imagen actual
        actual = self.actual #obtiene la animacion actual
        return actual.imagen if actual else None

    @property
    def termino(self): 
        #dice si la animacion actual ha terminado
        actual = self.actual
        return actual.termino if actual else True

    @property
    def lado(self): 
        #retorna el tamaño del frame
        actual = self.actual
        return actual.lado if actual else 0
    #endregion

    def actualizar(self, dt): 
        #actualiza la animacion
        actual = self.actual
        if actual:
            actual.actualizar(dt)
