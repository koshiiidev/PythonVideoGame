"""
Estado del juego es lo que sobrevive al cambio de escena

Si el dato tiene que seguir existiendo cuando se cambia de nivel o a otra escena va aqui, si solo le importa a una escena entonces va dentro de ella
"""

from config import settings as ajustes


class EstadoJuego(object):

    def __init__(self):
        #region Progreso
        self.nivel_actual = ajustes.NIVEL_INICIAL
        # Dónde aparece el jugador al entrar al nivel en tiles
        # None = usa el JUGADOR_INICIO que tenga el nivel
        self.entrada = None
        # Cosas que el juego tiene que recordar
        self.banderas = {}
        #endregion

        #region Preferencias de sesion
        self.mostrar_rejilla = False
        #endregion

    def bandera(self, nombre, valor=None):
        #lee una bandera o la escribe si se pasa un valor
        if valor is None:
            return self.banderas.get(nombre, False)
        self.banderas[nombre] = valor
        return valor

    def reiniciar(self):
        # Vuelve todo al principio para Partida nueva desde el menú
        self.nivel_actual = ajustes.NIVEL_INICIAL
        self.entrada = None
        self.banderas.clear()
