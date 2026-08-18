"""
Estado del juego es lo que sobrevive al cambio de escena

Si el dato tiene que seguir existiendo cuando se cambia de nivel o a otra escena va aqui,
si solo importa en una escena entonces va dentro de ella
"""

from config import settings as ajustes
from src.core import estadisticas
from src.core.jugador import Jugador


class EstadoJuego(object):

    def __init__(self):
        #region Configuracion

        self.nivel_actual = ajustes.NIVEL_INICIAL
        # Dónde aparece el jugador al entrar al nivel en tiles
        # None = usa el JUGADOR_INICIO que tenga el nivel
        self.entrada = None
        # Cosas que el juego tiene que recordar
        self.banderas = {}

        #preferencias de partida
        self.dificultad = ajustes.DIFICULTAD_POR_DEFECTO
        self.vidas = ajustes.VIDAS_POR_DEFECTO
        self.nombre = ajustes.NOMBRE_POR_DEFECTO
        self.icono = ajustes.ICONOS_JUGADOR[0]

        #Partida
        self.jugador = None

        #preferencias de sesion
        self.mostrar_rejilla = False
        #endregion

    #region Banderas
    def bandera(self, nombre, valor=None):
        #lee una bandera o la escribe si se pasa un valor
        if valor is None:
            return self.banderas.get(nombre, False)
        self.banderas[nombre] = valor
        return valor
    #endregion

    #region Configuracion
    def set_dificultad(self, nombre):
        if nombre not in ajustes.DIFICULTADES:
            raise ValueError('Dificultad desconocida: %r' % (nombre,))
        self.dificultad = nombre
        return self.dificultad

    def set_vidas(self, cantidad):
        cantidad = int(cantidad)
        if cantidad not in ajustes.VIDAS_OPCIONES:
            raise ValueError('Cantidad de vidas no permitida: %r' % (cantidad,))
        self.vidas = cantidad
        return self.vidas

    def configurar_jugador(self, nombre, icono):
        #Guarda nombre e icono. Valida antes de aceptar
        nombre = (nombre or '').strip()
        if not nombre:
            raise ValueError('El nombre no puede estar vacio')
        if len(nombre) > ajustes.LARGO_MAX_NOMBRE:
            raise ValueError('Maximo %d caracteres' % ajustes.LARGO_MAX_NOMBRE)
        if icono not in ajustes.ICONOS_JUGADOR:
            raise ValueError('Icono desconocido: %r' % (icono,))
        self.nombre = nombre
        self.icono = icono
        return self.nombre

    @property
    def ajuste_dificultad(self):
        #la dificultad elegida, enemigos, velocidad, etc
        return ajustes.DIFICULTADES[self.dificultad]
    #endregion

    #region Partida
    def iniciar_partida(self):
        #Crea el jugador con la configuracion actual y arranca de cero
        self.jugador = Jugador(self.nombre, self.icono, self.vidas)
        self.nivel_actual = ajustes.NIVEL_INICIAL
        self.entrada = None
        self.banderas.clear()
        return self.jugador

    @property
    def partida_terminada(self):
        return self.jugador is not None and self.jugador.esta_fuera

    def cerrar_partida(self):
        #Guarda las estadisticas y devuelve record, nombre, es_nuevo
        if self.jugador is None:
            return 0, '', False
        return estadisticas.registrar_partida(self.jugador.resumen(), self.dificultad)
    #endregion

    def reiniciar(self):
        # Vuelve todo al principio para Partida nueva desde el menú
        self.nivel_actual = ajustes.NIVEL_INICIAL
        self.entrada = None
        self.banderas.clear()
        self.jugador = None
