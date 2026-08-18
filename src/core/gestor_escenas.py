"""
Gestor de escenas

es una pantalla del juego: la cinemática, el menú, la partida, una
pausa. Solo la escena de mas arriba de la pila le llegan los eventos y se actualiza

Se usa una pila y no una sola escena para que se puedan superponer, como la pausa que se
apila sobre la partida, y al cerrarla vuelve la pantalla exactamente donde estaba.
"""


class Escena(object):
    """Clase base de aqui cada escena hereda y ya luego se redefine lo que se ocupe"""

    def __init__(self, gestor):
        self.gestor = gestor
        # Si es True la escena de abajo se sigue dibujando debajo
        self.transparente = False

    def entrar(self):
        #Se llama cuando la escena pasa a estar activa
        pass

    def salir(self):
        #Se llama cuando la escena deja de estar activa
        pass

    def manejar_evento(self, evento):
        #Se encarga de manejar eventos del teclado o mouse
        pass

    def actualizar(self, dt):
        #Se encarga de actualizar la logica de la escena
        pass

    def dibujar(self, pantalla):
        #Se encarga de dibujar la escena en la pantalla
        pass


class GestorEscenas(object):

    def __init__(self, pantalla, estado=None, audio=None):
        self.pantalla = pantalla
        self.estado = estado
        self.audio = audio
        self.pila = []
        self.corriendo = True

    @property
    def actual(self):
        return self.pila[-1] if self.pila else None

    #region Manejo de la pila
    def cambiar(self, escena):
        #Reemplaza toda la pila. como cuando pasa de menú a la partida
        while self.pila:
            self.pila.pop().salir()
        self.pila.append(escena)
        escena.entrar()

    def apilar(self, escena):
        #Pone una escena encima sin cerrar la de abajo
        self.pila.append(escena)
        escena.entrar()

    def desapilar(self):
        #Cierra la escena de arriba y vuelve a la anterior
        if self.pila:
            self.pila.pop().salir()
        if not self.pila:
            self.corriendo = False

    def terminar(self):
        #Cierra el juego
        while self.pila:
            self.pila.pop().salir()
        self.corriendo = False
    #endregion

    #region Datos del bucle
    def manejar_evento(self, evento):
        if self.actual:
            self.actual.manejar_evento(evento)

    def actualizar(self, dt):
        if self.actual:
            self.actual.actualizar(dt)

    def dibujar(self):
        if not self.pila:
            return
        # Se dibuja desde la primera escena no transparente hacia arriba, para
        # que en pausa se pueda ver el juego atras
        desde = len(self.pila) - 1
        while desde > 0 and self.pila[desde].transparente:
            desde -= 1
        for escena in self.pila[desde:]:
            escena.dibujar(self.pantalla)
    #endregion
