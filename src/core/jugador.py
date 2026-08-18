"""
Datos de un jugador durante la partida

    nombre e icono
    control de vidas
    puntaje y perdida de vida
    puntos por vida, adversarios eliminados y tiempo
    todo lo que necesita el resumen final
No dibuja nada esto
"""

from config import settings as ajustes


class Jugador(object):

    def __init__(self, nombre, icono, vidas=None):
        #region Validaciones
        nombre = (nombre or '').strip()
        if not nombre:
            raise ValueError('El nombre del jugador no puede estar vacio')
        if len(nombre) > ajustes.LARGO_MAX_NOMBRE:
            nombre = nombre[:ajustes.LARGO_MAX_NOMBRE]
        if icono not in ajustes.ICONOS_JUGADOR:
            raise ValueError('Icono desconocido: %r' % (icono,))

        vidas = ajustes.VIDAS_POR_DEFECTO if vidas is None else int(vidas)
        if vidas < 1:
            raise ValueError('Un jugador necesita al menos una vida')
        #endregion

        self.nombre = nombre
        self.icono = icono
        self.vidas_iniciales = vidas
        self.vidas = vidas

        #region Marcadores
        self.puntos = 0
        self.eliminados = 0
        self.tiempo = 0.0                 # segundos jugados por este jugador
        self.puntos_por_vida = []         # se cierra un tramo al perder cada vida
        self._puntos_vida_actual = 0
        #endregion

    #region Consultas
    @property
    def vidas_perdidas(self):
        return self.vidas_iniciales - self.vidas

    @property
    def record_por_vida(self):
        #El mejor tramo de puntos logrado con una sola vida 
        tramos = self.puntos_por_vida + [self._puntos_vida_actual]
        return max(tramos) if tramos else 0

    @property
    def esta_fuera(self):
        return self.vidas <= 0

    @property
    def promedio_por_vida(self):
        usadas = max(1, self.vidas_perdidas)
        return self.puntos / float(usadas)
    #endregion

    #region Acciones
    def sumar_puntos(self, cantidad):
        #Suma al total y al tramo de la vida en curso
        cantidad = int(cantidad)
        if cantidad < 0:
            raise ValueError('Los puntos no pueden ser negativos')
        self.puntos += cantidad
        self._puntos_vida_actual += cantidad
        return self.puntos

    def registrar_eliminacion(self, puntos=None):
        #Un enemigo menos - devuelve los puntos que le dio
        self.eliminados += 1
        pts = ajustes.PUNTOS_POR_ENEMIGO if puntos is None else puntos
        self.sumar_puntos(pts)
        return pts

    def perder_vida(self):
        #Cierra el tramo de puntos de esta vida y descuenta una
        #Devuelve True si el jugador quedo fuera
        if self.esta_fuera:
            return True
        self.vidas -= 1
        self.puntos_por_vida.append(self._puntos_vida_actual)
        self._puntos_vida_actual = 0
        return self.esta_fuera

    def sumar_tiempo(self, dt):
        self.tiempo += max(0.0, dt)
    #endregion

    #region Salida
    def resumen(self):
        return {
            'nombre': self.nombre,
            'icono': self.icono,
            'vidas_perdidas': self.vidas_perdidas,
            'vidas_restantes': self.vidas,
            'eliminados': self.eliminados,
            'puntos': self.puntos,
            'record_por_vida': self.record_por_vida,
            'tiempo': round(self.tiempo, 1),
        }

    def __repr__(self):
        return '<Jugador %s puntos=%d vidas=%d>' % (self.nombre, self.puntos, self.vidas)
    #endregion
