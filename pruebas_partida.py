"""
Pruebas del modelo de partida. No necesita pygame ni abrir ventana.

    python pruebas_partida.py

Cubre la validacion de datos (nombre, icono, dificultad, vidas), el conteo de
puntos y vidas, y la persistencia del record global, incluido el caso de
archivo corrupto.
"""

import os
import sys
import tempfile

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from config import settings as ajustes
# El archivo de prueba va al temporal del sistema: asi no ensucia datos/ ni
# depende de tener permiso de borrado en la carpeta del proyecto
ajustes.ARCHIVO_ESTADISTICAS = os.path.join(tempfile.gettempdir(),
                                            'cholito_estadisticas_prueba.json')

from src.core import estadisticas
from src.core.estado import EstadoJuego
from src.core.jugador import Jugador

ICONO = ajustes.ICONOS_JUGADOR[0]
OTRO_ICONO = ajustes.ICONOS_JUGADOR[2]

ok = fallos = 0


def chk(cond, msg):
    global ok, fallos
    if cond:
        ok += 1
    else:
        fallos += 1
        print('   FALLO:', msg)


def limpiar():
    #Deja el archivo de prueba en blanco. Si no se puede borrar, se sobrescribe
    try:
        if os.path.exists(ajustes.ARCHIVO_ESTADISTICAS):
            os.remove(ajustes.ARCHIVO_ESTADISTICAS)
    except OSError:
        with open(ajustes.ARCHIVO_ESTADISTICAS, 'w', encoding='utf-8') as f:
            f.write('{}')


print('== Jugador: validaciones ==')
for nombre, icono, caso in [('', ICONO, 'nombre vacio'),
                            ('   ', ICONO, 'nombre en blanco'),
                            ('Ana', 'inexistente.png', 'icono inventado')]:
    try:
        Jugador(nombre, icono)
        chk(False, 'acepto ' + caso)
    except ValueError:
        chk(True, '')
print('   nombre vacio, en blanco e icono invalido rechazados')

try:
    Jugador('Ana', ICONO, 0)
    chk(False, 'acepto cero vidas')
except ValueError:
    chk(True, '')
print('   cero vidas rechazado')

print('== Jugador: puntos, vidas y tramos ==')
j = Jugador('Luis', ICONO, 3)
for _ in range(4):
    j.registrar_eliminacion()
chk(j.puntos == 400 and j.eliminados == 4, 'puntos o eliminados mal')
chk(j.record_por_vida == 400, 'record por vida mal')

fuera = j.perder_vida()
chk(not fuera and j.vidas == 2 and j.vidas_perdidas == 1, 'perder_vida mal')
chk(j.puntos_por_vida == [400], 'no cerro el tramo de la vida')

j.registrar_eliminacion()
chk(j.record_por_vida == 400, 'el record por vida deberia seguir en 400')

j.perder_vida()
fuera = j.perder_vida()
chk(fuera and j.esta_fuera, 'no quedo fuera al agotar las vidas')
chk(j.perder_vida() is True, 'perder vida estando fuera deberia ser inocuo')
print('   puntos %d, eliminados %d, tramos %s' % (j.puntos, j.eliminados, j.puntos_por_vida))

try:
    j.sumar_puntos(-5)
    chk(False, 'acepto puntos negativos')
except ValueError:
    chk(True, '')
print('   puntos negativos rechazados')

print('== EstadoJuego: configuracion ==')
e = EstadoJuego()
for metodo, valor, caso in [(e.set_dificultad, 'Imposible', 'dificultad'),
                            (e.set_vidas, 99, 'vidas')]:
    try:
        metodo(valor)
        chk(False, 'acepto %s invalida' % caso)
    except ValueError:
        chk(True, '')
print('   dificultad y vidas fuera de rango rechazadas')

e.set_dificultad('Leyenda')
e.set_vidas(5)
chk(e.ajuste_dificultad['enemigos'] == 8, 'ajuste de dificultad mal')
print('   Leyenda ->', e.ajuste_dificultad)

try:
    e.configurar_jugador('  ', ICONO)
    chk(False, 'acepto nombre en blanco')
except ValueError:
    chk(True, '')
try:
    e.configurar_jugador('EsteNombreEsDemasiadoLargo', ICONO)
    chk(False, 'acepto nombre largo')
except ValueError:
    chk(True, '')
e.configurar_jugador('  Luis  ', OTRO_ICONO)
chk(e.nombre == 'Luis' and e.icono == OTRO_ICONO, 'no guardo la configuracion')
print('   configuracion guardada:', e.nombre, e.icono)

print('== EstadoJuego: partida ==')
chk(e.jugador is None and not e.partida_terminada, 'no deberia haber partida todavia')
j = e.iniciar_partida()
chk(j.nombre == 'Luis' and j.vidas == 5, 'la partida no tomo la configuracion')
print('   partida iniciada:', j)

j.registrar_eliminacion()
j.registrar_eliminacion()
j.sumar_tiempo(12.5)
while not j.esta_fuera:
    j.perder_vida()
chk(e.partida_terminada, 'no detecto el fin de la partida')
print('   fin de partida con %d puntos y %d eliminados' % (j.puntos, j.eliminados))

print('== Estadisticas persistentes ==')
limpiar()
rec, nom, nuevo = e.cerrar_partida()
chk(nuevo and rec == 200 and nom == 'Luis', 'record mal: %s %s %s' % (rec, nom, nuevo))
print('   record global:', rec, 'de', nom, '| nuevo:', nuevo)

rec2, nom2 = estadisticas.record_global()
chk(rec2 == 200 and nom2 == 'Luis', 'no persistio el record')
print('   releido del archivo:', rec2, nom2)

# Una partida peor no debe pisar el record
e.iniciar_partida()
e.jugador.registrar_eliminacion()
while not e.jugador.esta_fuera:
    e.jugador.perder_vida()
rec3, nom3, nuevo3 = e.cerrar_partida()
chk(not nuevo3 and rec3 == 200, 'una partida peor piso el record')
print('   partida peor -> record sigue en', rec3)

with open(ajustes.ARCHIVO_ESTADISTICAS, 'w', encoding='utf-8') as f:
    f.write('{ esto no es json valido')
datos = estadisticas.cargar()
chk(datos['record_global'] == 0, 'no se recupero del archivo corrupto')
print('   archivo corrupto -> arranca en 0 sin caerse')
limpiar()

print()
print('PRUEBAS: %d bien, %d mal' % (ok, fallos))
sys.exit(1 if fallos else 0)
