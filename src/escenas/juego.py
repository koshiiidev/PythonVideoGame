"""
El juego en si

Se carga el nivel por nombre y se puede cambiar la escena en caliente
"""

import math
import random
import pygame

from config import settings as ajustes
from src.core import recursos
from src.core import cargador_niveles
from src.core import geometria
from src.core.autotile import Terreno
from src.core.animacion import Animacion
from src.core.enemigo import Enemigo
from src.core.gestor_escenas import Escena
from src.escenas.hud import Hud


class EscenaJuego(Escena):

    def __init__(self, gestor, paseo=False):
        Escena.__init__(self, gestor)
        self.estado = gestor.estado
        self.audio = gestor.audio

        # MODO PASEO: sirve para revisar un mapa sin jugarlo
        self.paseo = bool(paseo)

        self.font = pygame.font.SysFont(None, 24)
        self.font_rejilla = pygame.font.SysFont(None, 16)
        self._cache_rejilla = {}

        #region Assets
        # Carga TODOS los terrenos de assets/tiles/terreno. Camino, tierra,
        # agua, cerca y muro entran por el mismo camino: cada uno es una
        # carpeta con sus 16 tiles
        self.terreno = Terreno(ajustes.DIR_TERRENO, escala=ajustes.TILE_W)
        self.jugador_frames = self._cargar_animaciones('%s_sp.png')
        self.ataque_frames = self._cargar_animaciones('%s_ataque_sp.png')
        self.hud = Hud()
        #endregion

        #region Estado de la partida
        self.nivel = None
        self.objeto_images = {}
        self.npcs = []
        self.jugador = {
            'x': 0, 'y': 0,
            'velocidad': ajustes.VELOCIDAD_JUGADOR,
            'direccion': 'frente',
            'moviendose': False,
            'atacando': False,
        }
        self.camera = {'x': 0, 'y': 0}
        self.teclas = {'up': False, 'down': False, 'left': False, 'right': False}

        self.frame_idx = 0
        self.t_frame = 0.0
        self.ataque_idx = 0
        self.t_ataque = 0.0
        self.ataque_listo = True

        # tile en que esta el jugador para que no se ejecute varias veces la el cambio de mapa por los frames
        self.tile_previo = None
        #endregion

        #region Combate
        self.enemigos = []
        self.t_invulnerable = 0.0     # mientras sea > 0 no recibe daño
        self.hacia_el_bono = 0        # eliminados desde el ultimo bono
        self.eliminados_nivel = 0     # cuenta para el objetivo del nivel actual
        self.velocidad_extra = 0.0    # sube con cada bono (requisito 9)
        self.aviso = ''
        self.t_aviso = 0.0
        self.jefe = None              # el enemigo grande del nivel, si lo hay
        self.balas_bruja = []
        self.t_disparo_bruja = 0.0
        #endregion

    #region Carga
    def _cargar_animaciones(self, patron):
        codigos = {'frente': 'J1_F', 'espalda': 'J1_E',
                   'derecha': 'J1_D', 'izquierda': 'J1_I'}
        frames = {}
        for nombre, codigo in codigos.items():
            ruta = '%s/%s' % (ajustes.DIR_JUGADOR, patron % codigo)
            frames[nombre] = recursos.spritesheet(
                ruta, ajustes.FRAMES_ANIM,
                (ajustes.JUG_W, ajustes.JUG_H), ajustes.TILE_ORIG_W)
        return frames

    def entrar(self):
        self.cargar_nivel(self.estado.nivel_actual, self.estado.entrada)

    def cargar_nivel(self, nombre, entrada=None):
        #carga o cambia de mapa, entrada es (columna, fila) en tiles o None
        self.nivel = cargador_niveles.cargar(nombre)
        self.estado.nivel_actual = nombre

        # Suelo propio del nivel si lo declara
        self.suelo = None
        if self.nivel.suelo:
            suelo = Animacion(self.nivel.suelo, lado=ajustes.TILE_W)
            self.suelo = suelo.imagen

        # Objetos que ocupan mas de un tile se cargan aparte porque hay que respetarles la proporcion. Se guardan ya escalados
        self.objeto_images = {}       # caracter -> Animacion del tamano de un tile
        self.objeto_grandes = {}      # caracter -> imagen ya escalada, mas grande que el tile
        self.objeto_profundos = set() # caracteres que se ordenan por profundidad
        for caracter, ruta in self.nivel.objetos.items():
            escala = self.nivel.altos.get(caracter)
            if escala:
                img = recursos.imagen(ruta)
                if img:
                    ancho = int(ajustes.TILE_W * escala)
                    alto = int(ancho * img.get_height() / float(img.get_width()))
                    self.objeto_grandes[caracter] = pygame.transform.scale(
                        img, (ancho, alto))
                # Si se desborda de su casilla hay que ordenarlo si o si, o
                # taparia al jugador estando el jugador mas adelante
                self.objeto_profundos.add(caracter)
                continue
            anim = Animacion(ruta, lado=ajustes.TILE_W, fps=ajustes.FPS_OBJETO)
            if anim.frames:
                self.objeto_images[caracter] = anim
        # Y los que miden un tile pero el nivel pide ordenar igual (los arboles)
        self.objeto_profundos |= set(self.nivel.profundidad)

        # NPCs: las posiciones vienen en tiles y aqui se pasan a pixeles
        self.npcs = []
        for datos in self.nivel.npcs: # por cada npc en el nivel
            img = recursos.imagen('%s/%s' % (ajustes.DIR_NPC, datos['sprite']),
                                (ajustes.JUG_W, ajustes.JUG_H)) # carga la imagen
            if not img: 
                continue # si la imagen no se cargo correctamente se salta el npc
            self.npcs.append({
                'sprite': img,
                'x': datos['x'] * ajustes.TILE_W,
                'y': datos['y'] * ajustes.TILE_H,
                'solido': datos.get('solido', True), # los npcs son solidos por defecto
            })

        self._ubicar_jugador(entrada)
        self._cache_rejilla.clear()
        self.enemigos = []
        self.eliminados_nivel = 0
        self.jefe = None
        self.balas_bruja = []
        self.t_disparo_bruja = 0.0
        self.poblar_enemigos()
        self.invocar_jefe()

        if self.audio and self.nivel.musica:
            self.audio.musica(self.nivel.musica)

    def _ubicar_jugador(self, entrada):
        destino = entrada or self.nivel.inicio
        if destino: # si hay una entrada definida
            self.jugador['x'] = destino[0] * ajustes.TILE_W 
            self.jugador['y'] = destino[1] * ajustes.TILE_H 
        else: # si no hay una entrada definida se posiciona en el centro del mapa
            self.jugador['x'] = self.ancho_mapa // 2 - ajustes.JUG_W // 2 
            self.jugador['y'] = self.alto_mapa // 2 - ajustes.JUG_H // 2
        self.estado.entrada = None
        self.tile_previo = self.tile_del_jugador()
        self.actualizar_camara()
    #endregion

    #region Medidas
    @property
    def ancho_mapa(self):
        return self.nivel.ancho_px(ajustes.TILE_W)

    @property
    def alto_mapa(self):
        return self.nivel.alto_px(ajustes.TILE_H)

    def tile_del_jugador(self):
        #Tile donde están los pies del jugador
        return (int((self.jugador['x'] + ajustes.JUG_W // 2) // ajustes.TILE_W),
                int((self.jugador['y'] + ajustes.JUG_H - 4) // ajustes.TILE_H))
    #endregion

    #region Hitbox y colision
    def hitbox_pies(self, pos_x, pos_y):
        #solo los pies para que el personaje se vea frente a los objetos
        return geometria.caja_pies_jugador(pos_x, pos_y)

    def centro_jugador(self):
        #Centro de la caja de pies, es el punto que persiguen los enemigos
        return self.hitbox_pies(self.jugador['x'], self.jugador['y']).center

    def hitbox_tile(self, col, fil):
        #la caja que bloquea en esa casilla
        prop_ancho, prop_alto, anclaje = self.nivel.colision(col, fil)
        return geometria.caja_celda(col, fil, prop_ancho, prop_alto, anclaje)

    def colisiona_con_mapa(self, rect_pies):
        tw, th = ajustes.TILE_W, ajustes.TILE_H
        #revisa una casilla de mas en cada lado por si los objetos son mas anchos que su propia casilla
        col_ini = int(max(0, rect_pies.left // tw - 1))
        col_fin = int(min(self.nivel.cols - 1, rect_pies.right // tw + 1))
        fil_ini = int(max(0, rect_pies.top // th - 1))
        fil_fin = int(min(self.nivel.filas - 1, rect_pies.bottom // th + 1))

        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                if self.nivel.es_solido(col, fil):
                    if rect_pies.colliderect(self.hitbox_tile(col, fil)):
                        return True
        return False

    def colisiona_con_npcs(self, rect_pies):
        for npc in self.npcs:
            if npc.get('solido', False):
                if rect_pies.colliderect(
                        geometria.caja_pies_jugador(npc['x'], npc['y'])):
                    return True
        return False
    #endregion

    #region Eventos
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_p):
                # Se apila: la partida queda congelada debajo, sin perder nada
                from src.escenas.pausa import EscenaPausa
                self.gestor.apilar(EscenaPausa(self.gestor, self))
                
            elif evento.key == pygame.K_g and ajustes.MOSTRAR_DEPURACION:
                #La rejilla es de depuración si está apagada, la tecla no hace nada
                self.estado.mostrar_rejilla = not self.estado.mostrar_rejilla
            elif evento.key == pygame.K_SPACE and self.ataque_listo:
                self.ataque_idx = 0
                self.t_ataque = 0.0
                self.ataque_listo = False
                self.jugador['atacando'] = True
                self.atacar()
                if self.audio:
                    self.audio.sfx('espada.wav') #todavia no esta este audio

    #endregion


    #region Enemigos y combate
    def tiles_libres(self):
        #Casillas donde un enemigo puede aparecer sin quedar dentro de una pared
        libres = []
        for fil in range(self.nivel.filas):
            for col in range(self.nivel.cols):
                if not self.nivel.es_solido(col, fil) and not self.nivel.salida_en(col, fil):
                    libres.append((col, fil))
        return libres

    def poblar_enemigos(self):
        #Mantiene la cantidad de enemigos de la dificultad
        if self.paseo:              # si es modo paseo no carga enemigos
            self.enemigos = []
            return
        objetivo = self.estado.ajuste_dificultad['enemigos']
        vivos = [e for e in self.enemigos if e.vivo]
        self.enemigos = vivos
        # El jefe no entra en la cuenta es unico y no se repone
        if self.hay_jefe and self.jefe.vivo:
            objetivo += 1
        intentos = 0
        while len(self.enemigos) < objetivo and intentos < 60:
            intentos += 1
            if self.aparecer_enemigo():
                continue

    def aparecer_enemigo(self):
        #Aparece uno nuevo lejos del jugador
        libres = self.tiles_libres()
        if not libres:
            return False
        col, fil = random.choice(libres)
        # Cada criatura tiene su propio tamano
        tipo = self.nivel.enemigo
        lado = ajustes.ENEMIGOS.get(tipo, {}).get('lado', ajustes.ENEMIGO_LADO)
        x = col * ajustes.TILE_W + (ajustes.TILE_W - lado) // 2
        # La base del enemigo se apoya en el piso del tile igual que el jugador
        #si no sus hitbox nunca se tocan
        y = fil * ajustes.TILE_H + ajustes.TILE_H - lado
        if math.hypot(x - self.jugador['x'], y - self.jugador['y']) < ajustes.DISTANCIA_APARICION:
            return False
        # Tampoco encima de otro
        for otro in self.enemigos:
            if otro.vivo and math.hypot(x - otro.x, y - otro.y) < ajustes.SEPARACION_ENEMIGOS:
                return False
        ajuste = self.estado.ajuste_dificultad
        self.enemigos.append(Enemigo(
            x, y, tipo,
            velocidad=ajuste['velocidad'] + self.velocidad_extra,
            dano=ajuste['dano'],
            puntos=int(ajustes.PUNTOS_POR_ENEMIGO * ajuste['multiplicador'])))
        return True

    def actualizar_enemigos(self, dt):
        objetivo = self.centro_jugador()
        for enemigo in self.enemigos:
            enemigo.actualizar(dt, objetivo, self.colisiona_con_mapa)
            if self.t_invulnerable <= 0 and enemigo.toca(self.hitbox_pies(
                    self.jugador['x'], self.jugador['y'])):
                self.recibir_dano(enemigo.dano)
        self.poblar_enemigos()

    def rect_ataque(self):
        #Caja del machetazo delante del jugador segun su direccion
        largo, ancho = ajustes.ALCANCE_ATAQUE, ajustes.ANCHO_ATAQUE
        cx = self.jugador['x'] + ajustes.JUG_W // 2
        cy = self.jugador['y'] + ajustes.JUG_H // 2
        direccion = self.jugador['direccion']
        if direccion == 'espalda':
            return pygame.Rect(cx - ancho // 2, cy - largo, ancho, largo)
        if direccion == 'frente':
            return pygame.Rect(cx - ancho // 2, cy, ancho, largo)
        if direccion == 'izquierda':
            return pygame.Rect(cx - largo, cy - ancho // 2, largo, ancho)
        return pygame.Rect(cx, cy - ancho // 2, largo, ancho)

    def atacar(self):
        #Resuelve el machetazo contra todos los enemigos alcanzados
        caja = self.rect_ataque()
        jugador = self.estado.jugador
        for enemigo in self.enemigos:
            if enemigo.vivo and enemigo.rect.colliderect(caja):
                # Se le pasa la posicion del jugador para saber hacia donde sale despedido
                origen = self.centro_jugador()
                if enemigo.recibir_golpe(1, desde=origen) and jugador:
                    jugador.registrar_eliminacion(enemigo.puntos)
                    if enemigo is self.jefe:
                        nombre = (self.nivel.jefe or {}).get('nombre', 'La Cangreja')
                        self.mostrar_aviso('¡%s cae!' % nombre, 3.0)
                    else:
                        self.eliminados_nivel += 1
                    self.revisar_bono()
                    self.revisar_objetivo()
                    if self.audio:
                        self.audio.sfx('enemigo.wav')

    def revisar_bono(self):
        #Cada cierta cantidad de eliminados puntos extra y enemigos mas rapidos
        self.hacia_el_bono += 1
        if self.hacia_el_bono < ajustes.ENEMIGOS_PARA_BONO:
            return
        self.hacia_el_bono = 0
        self.velocidad_extra += ajustes.VELOCIDAD_POR_BONO
        for enemigo in self.enemigos:
            enemigo.velocidad += ajustes.VELOCIDAD_POR_BONO
        if self.estado.jugador:
            self.estado.jugador.sumar_puntos(ajustes.PUNTOS_BONO)
        self.mostrar_aviso('¡BONO! +%d  ·  la niebla se agita' % ajustes.PUNTOS_BONO)
        if self.audio:
            self.audio.sfx('bono.wav')

    def recibir_dano(self, dano=1):
        #Quita una vida, da unos segundos de invulnerabilidad y aleja al jugador
        jugador = self.estado.jugador
        if self.paseo or jugador is None or self.t_invulnerable > 0:
            return
        self.t_invulnerable = ajustes.INVULNERABLE_S
        sin_vidas = jugador.perder_vida()
        if self.audio:
            self.audio.sfx('dano.wav')
        if sin_vidas:
            self.terminar_partida()
        else:
            self.mostrar_aviso('Perdiste una vida')
            self._ubicar_jugador(self.nivel.inicio)
            # Se limpian las sombras para dar aire al volver
            self.enemigos = [self.jefe] if (self.hay_jefe and self.jefe.vivo) else []
            if self.hay_jefe and self.jefe.vivo:
                # Lo devuelve a su sitio para que no reaparezca encima
                self._reubicar_jefe()
            self.poblar_enemigos()

    def _reubicar_jefe(self):
        #Vuelve al punto donde lo puso el nivel y se le quita el aturdimiento
        ficha = self.nivel.jefe or {}
        tw, th = ajustes.TILE_W, ajustes.TILE_H
        if 'x' in ficha and 'y' in ficha:
            self.jefe.x = ficha['x'] * tw + (tw - self.jefe.lado) // 2
            self.jefe.y = ficha['y'] * th + th - self.jefe.lado
        self.jefe.t_retroceso = 0.0
        self.jefe.t_aturdido = 0.0

    def terminar_partida(self):
        from src.escenas.resultados import EscenaResultados
        self.gestor.cambiar(EscenaResultados(self.gestor, victoria=False))

    def _por_que_no_puede_salir(self):
        if self.hay_jefe and self.jefe.vivo:
            return 'La bruja no te deja ir.'
        if self.faltan == 1:
            return 'La niebla no deja pasar. Falta 1 sombra.'
        return f'La niebla no deja pasar. Faltan {self.faltan} sombras.'

    def mostrar_aviso(self, texto, segundos=2.0):
        self.aviso = texto
        self.t_aviso = segundos
    #endregion


    #region Jefe

    def disparar_bruja(self):
        if not self.hay_jefe or not self.jefe.vivo:
            return
        # Posición de la bruja
        bruja_x, bruja_y = self.jefe.centro
        jugador_x, jugador_y = self.centro_jugador()
        diferencia_x = jugador_x - bruja_x
        diferencia_y = jugador_y - bruja_y

        distancia = math.sqrt(
            math.pow(diferencia_x, 2) +
            math.pow(diferencia_y, 2)
        )

        if distancia == 0:
            return

        direccion_x = diferencia_x / distancia
        direccion_y = diferencia_y / distancia

        nueva_bala = {
            'x': bruja_x,
            'y': bruja_y,
            'velocidad_x': direccion_x,
            'velocidad_y': direccion_y
        }

        self.balas_bruja.append(nueva_bala)
        
    def hay_colision_bala(self, x_1, y_1, x_2, y_2):
        distancia = math.sqrt(
            math.pow(x_2 - x_1, 2) +
            math.pow(y_2 - y_1, 2)
        )
        if distancia < 27:
            return True
        else:
            return False    

    def actualizar_balas_bruja(self, dt):
        velocidad_bala = 250
        jugador_x, jugador_y = self.centro_jugador()
        
        for bala in self.balas_bruja:
            bala['x'] += bala['velocidad_x'] * velocidad_bala * dt
            bala['y'] += bala['velocidad_y'] * velocidad_bala * dt

            colision = self.hay_colision_bala(
                jugador_x,
                jugador_y,
                bala['x'],
                bala['y']
            )
            
            if colision:
                self.balas_bruja.remove(bala)
                self.recibir_dano()
                break
                
            #Eliminar bala fuera del mapa    
            if (bala['x'] < 0 or
                    bala['x'] > self.ancho_mapa or
                    bala['y'] < 0 or
                    bala['y'] > self.alto_mapa):
                        
                self.balas_bruja.remove(bala)

    def dibujar_balas_bruja(self, pantalla):
        for bala in self.balas_bruja:
            x = int(bala['x'] - self.camera['x'])
            y = int(bala['y'] - self.camera['y'])
            pygame.draw.circle(
                pantalla,
                (180, 50, 220),
                (x, y),
                8
            )
    def actualizar_disparo_bruja(self, dt):
        if not self.hay_jefe or not self.jefe.vivo:
            return
        self.t_disparo_bruja += dt

        if self.t_disparo_bruja >= 2.0:
            self.disparar_bruja()
            self.t_disparo_bruja = 0.0
            
    def invocar_jefe(self):
        #Lo trae el nivel, con su vida y su velocidad propias. Aparece donde el
        #nivel diga; si no dice nada, en el centro del mapa
        ficha = self.nivel.jefe
        if not ficha or self.paseo: #si es modo paseo no carga jefe
            return

        tw, th = ajustes.TILE_W, ajustes.TILE_H
        tipo = ficha.get('tipo', 'bruja')
        lado = ajustes.ENEMIGOS.get(tipo, {}).get('lado', ajustes.ENEMIGO_LADO)

        if 'x' in ficha and 'y' in ficha:
            x = ficha['x'] * tw + (tw - lado) // 2
            y = ficha['y'] * th + th - lado
        else:
            x = self.ancho_mapa // 2 - lado // 2
            y = self.alto_mapa // 2 - lado // 2

        # La dificultad lo afecta en Leyenda pega mas fuerte y corre mas
        ajuste = self.estado.ajuste_dificultad
        self.jefe = Enemigo(
            x, y, tipo,
            velocidad=ficha.get('velocidad', 70) + self.velocidad_extra,
            vida=int(ficha.get('vida', 10) * ajuste.get('multiplicador', 1.0)),
            dano=ficha.get('dano', 1),
            puntos=int(ficha.get('puntos', 3000) * ajuste.get('multiplicador', 1.0)))
        self.enemigos.append(self.jefe)
        self.mostrar_aviso(ficha.get('nombre', 'La Bruja despierta'), 3.0)

    @property
    def hay_jefe(self):
        return self.jefe is not None

    @property
    def jefe_vencido(self):
        return self.hay_jefe and not self.jefe.vivo
    #endregion

    #region Objetivo del nivel y victoria
    @property
    def nivel_despejado(self):
        #Un nivel sin objetivo esta despejado desde el principio.
        #Si ademas tiene jefe, hay que vencerlo.
        if self.paseo:              # paseando se puede cruzar cualquier puerta
            return True
        if self.hay_jefe and not self.jefe_vencido:
            return False
        return self.eliminados_nivel >= self.nivel.objetivo

    @property
    def faltan(self):
        return max(0, self.nivel.objetivo - self.eliminados_nivel)

    def revisar_objetivo(self):
        #Se llama al eliminar un enemigo: avisa cuando el nivel queda despejado
        if not self.nivel_despejado:
            return
        # Solo la primera vez que se cumple, no en cada golpe posterior
        if self.eliminados_nivel > self.nivel.objetivo:
            return
        if self.nivel.objetivo <= 0 and not self.hay_jefe:
            return
        if self.nivel.es_final:
            self.ganar()
        else:
            self.mostrar_aviso('La niebla se abre. El camino está libre.', 3.0)
            if self.audio:
                self.audio.sfx('camino.wav')

    def ganar(self):
        #Despejar el nivel final cierra la historia
        from src.escenas.cinematica import EscenaCinematica, FINAL
        from src.escenas.resultados import EscenaResultados

        def al_terminar():
            self.gestor.cambiar(EscenaResultados(self.gestor, victoria=True))

        self.gestor.cambiar(EscenaCinematica(self.gestor, FINAL,
                                             al_terminar=al_terminar))
    #endregion

    #region Actualizacion
    def actualizar(self, dt):
        self.leer_teclado()
        self.mover(dt)
        self.revisar_salida()
        self.actualizar_enemigos(dt)
        self.actualizar_balas_bruja(dt)
        self.actualizar_disparo_bruja(dt)
        self.actualizar_camara()
        self.animar(dt)
        self.animar_objetos(dt)
        self._contar_tiempo(dt)
        if self.t_aviso > 0:
            self.t_aviso = max(0.0, self.t_aviso - dt)

    def sprite_objeto(self, caracter):
        #El dibujo actual de un objeto, venga de una imagen escalada (ALTOS) o
        #de una animacion del tamano del tile. Asi el resto del codigo no tiene
        #que preguntar de cual de los dos se trata
        if caracter in self.objeto_grandes:
            return self.objeto_grandes[caracter]
        animacion = self.objeto_images.get(caracter)
        return animacion.imagen if animacion else None

    def animar_objetos(self, dt):
        for anim in self.objeto_images.values():
            anim.actualizar(dt)

    def _contar_tiempo(self, dt):
        #El tiempo jugado es parte del resumen final
        if self.estado.jugador:
            self.estado.jugador.sumar_tiempo(dt)
        if self.t_invulnerable > 0:
            self.t_invulnerable = max(0.0, self.t_invulnerable - dt)

    def leer_teclado(self):
        #Se le pregunta el estado real al teclado en cada frame, en vez de
        #llevarlo a mano con KEYDOWN/KEYUP. Asi, si la ventana pierde el foco
        #con una tecla apretada, el personaje no se queda caminando solo
        t = pygame.key.get_pressed()
        self.teclas['up'] = t[pygame.K_UP] or t[pygame.K_w]
        self.teclas['down'] = t[pygame.K_DOWN] or t[pygame.K_s]
        self.teclas['left'] = t[pygame.K_LEFT] or t[pygame.K_a]
        self.teclas['right'] = t[pygame.K_RIGHT] or t[pygame.K_d]

    def mover(self, dt):
        j = self.jugador
        # -1, 0 o 1 en cada eje. Sumar los dos permite caminar en diagonal
        dx = int(self.teclas['right']) - int(self.teclas['left'])
        dy = int(self.teclas['down']) - int(self.teclas['up'])
        j['moviendose'] = bool(dx or dy)

        if dx and dy:
            # En diagonal se avanza en los dos ejes a la vez. Sin corregir, el
            # recorrido seria 1.41 veces mas largo y el jugador iria mas rapido
            # en diagonal que en linea recta
            dx *= 0.7071
            dy *= 0.7071

        if dx:
            j['direccion'] = 'derecha' if dx > 0 else 'izquierda'
        elif dy:
            j['direccion'] = 'frente' if dy > 0 else 'espalda'

        paso = j['velocidad'] * dt
        nueva_x = j['x'] + dx * paso
        nueva_y = j['y'] + dy * paso

        # Cada eje se resuelve por separado
        if nueva_x != j['x']:
            nueva_x = max(0, min(self.ancho_mapa - ajustes.JUG_W, nueva_x))
            hb = self.hitbox_pies(nueva_x, j['y'])
            if not self.colisiona_con_mapa(hb) and not self.colisiona_con_npcs(hb):
                j['x'] = nueva_x

        if nueva_y != j['y']:
            nueva_y = max(0, min(self.alto_mapa - ajustes.JUG_H, nueva_y))
            hb = self.hitbox_pies(j['x'], nueva_y)
            if not self.colisiona_con_mapa(hb) and not self.colisiona_con_npcs(hb):
                j['y'] = nueva_y

    def revisar_salida(self):
        #Si el jugador acaba de entrar a un tile con salida cambia de nivel
        tile = self.tile_del_jugador()
        if tile == self.tile_previo: #evitar bucle o repetir la accion en cada frame
            return
        self.tile_previo = tile
        destino = self.nivel.salida_en(tile[0], tile[1])
        if destino:
            if not self.nivel_despejado:
                self.mostrar_aviso(self._por_que_no_puede_salir(), 2.5)
                return
            nombre, col, fil = destino
            if self.audio:
                self.audio.sfx('puerta.wav') #todavia no esta este audio
            self.cargar_nivel(nombre, (col, fil))

    def actualizar_camara(self):
        c, j = self.camera, self.jugador
        c['x'] = self.eje_camara(j['x'] + ajustes.JUG_W // 2,
                                 ajustes.ANCHO, self.ancho_mapa)
        c['y'] = self.eje_camara(j['y'] + ajustes.JUG_H // 2,
                                 ajustes.ALTO, self.alto_mapa)

    @staticmethod
    def eje_camara(centro, tam_pantalla, tam_mapa):
        #Un eje de la camara: cuanto hay que restarle al mundo para dibujarlo
        if tam_mapa <= tam_pantalla:
            # El mapa entra completo: se centra y no se mueve. Sale negativo a
            # proposito, asi el mapa se corre hacia adentro de la pantalla
            return -(tam_pantalla - tam_mapa) // 2
        # Mapa grande: sigue al jugador sin mostrar de mas por los bordes
        return max(0, min(tam_mapa - tam_pantalla, centro - tam_pantalla // 2))

    def animar(self, dt):
        self.t_frame += dt
        if self.t_frame >= 1.0 / ajustes.FPS_ANIM:
            self.frame_idx = ((self.frame_idx + 1) % ajustes.FRAMES_ANIM
                              if self.jugador['moviendose'] else 0)
            self.t_frame = 0.0

        if not self.ataque_listo:
            self.t_ataque += dt
            if self.t_ataque >= 1.0 / ajustes.FPS_ATAQUE:
                self.ataque_idx += 1
                if self.ataque_idx >= ajustes.FRAMES_ANIM:
                    self.ataque_idx = 0
                    self.ataque_listo = True
                    self.jugador['atacando'] = False
                self.t_ataque = 0.0
    #endregion

    #region Dibujo
    def dibujar(self, pantalla):
        pantalla.fill(ajustes.COLOR_FUERA_MAPA)
        rango = self.rango_visible()
        self.dibujar_terreno(pantalla, rango)
        self.dibujar_ordenados(pantalla, rango)
        self.dibujar_balas_bruja(pantalla)
        self.dibujar_rejilla(pantalla, rango)
        self.dibujar_colisiones(pantalla, rango)

        if ajustes.MOSTRAR_DEPURACION and self.jugador['atacando']:
            caja = self.rect_ataque()
            pygame.draw.rect(pantalla, (255, 240, 120),
                             (caja.x - self.camera['x'], caja.y - self.camera['y'],
                              caja.width, caja.height), 1)
        self.hud.dibujar(pantalla, self.estado.jugador)

        if self.hay_jefe and self.jefe.vivo:
            self.hud.barra_jefe(pantalla, self.jefe,
                                self.nivel.jefe.get('nombre', 'La Bruja'))

        if self.nivel.objetivo > 0 or self.hay_jefe:
            self.hud.objetivo(pantalla, self.faltan, self.nivel.titulo,
                              jefe_vivo=self.hay_jefe and self.jefe.vivo)
        
        if self.t_aviso > 0 and self.aviso:
            self.hud.aviso(pantalla, self.aviso)
        self.dibujar_info(pantalla)

    def rango_visible(self):
        #Solo se dibuja lo que entra en pantalla
        c = self.camera
        tw, th = ajustes.TILE_W, ajustes.TILE_H
        return (int(max(0, c['x'] // tw)),
                int(min(self.nivel.cols - 1, (c['x'] + ajustes.ANCHO) // tw + 1)),
                int(max(0, c['y'] // th)),
                int(min(self.nivel.filas - 1, (c['y'] + ajustes.ALTO) // th + 1)))

    def dibujar_terreno(self, pantalla, rango):
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                px = col * ajustes.TILE_W - camara['x']
                py = fil * ajustes.TILE_H - camara['y']
                caracter = self.nivel.celda(col, fil)

                # Debajo de todo va el suelo del nivel, o pasto si no declaro
                # uno. El pasto alterna variantes para no verse repetido
                pantalla.blit(
                    self.suelo or self.terreno.pasto_en(
                        col, fil, ajustes.PROB_VARIANTE_PASTO), (px, py))

                tipo_tile = self.nivel.terrenos.get(caracter)
                if tipo_tile:
                    # "continuan" hace que una puerta no corte el muro
                    sigue = self.nivel.continuan.get(caracter)
                    bitmask = self.terreno.bitmask(self.nivel.mapa, col, fil,
                                                   caracter, sigue)
                    pantalla.blit(self.terreno.tile(tipo_tile, bitmask), (px, py))
                    if tipo_tile == 'agua':
                        for e in self.terreno.recodos(self.nivel.mapa, col, fil,
                                                      caracter, bitmask, sigue):
                            pantalla.blit(self.terreno.agua_esq[e], (px, py))
                elif (caracter in self.objeto_images
                      and caracter not in self.objeto_profundos):
                    # .imagen sirve igual para un objeto quieto que para uno animado
                    #Aca solo van los PLANOS: los que se ordenan por
                    #profundidad se dibujan despues, con los personajes
                    pantalla.blit(self.objeto_images[caracter].imagen, (px, py))

                # Capa DECOR: lo que se para sobre el suelo. Va encima del
                # terreno, por eso se puede poner un barril en pleno camino
                adorno = self.nivel.adorno(col, fil)
                if (adorno in self.objeto_images
                        and adorno not in self.objeto_profundos):
                    pantalla.blit(self.objeto_images[adorno].imagen, (px, py))

    def dibujar_ordenados(self, pantalla, rango):
        #Personajes y obstáculos altos, ordenados por la Y de sus pies
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        elementos = []

        if self.jugador['atacando']:
            frames = self.ataque_frames[self.jugador['direccion']]
            sprite = frames[min(self.ataque_idx, len(frames) - 1)]
        else:
            frames = self.jugador_frames[self.jugador['direccion']]
            sprite = frames[min(self.frame_idx, len(frames) - 1)]

        #mientras es invulnerable parpadea
        parpadeo = (self.t_invulnerable > 0 and int(self.t_invulnerable * ajustes.PARPADEO_HZ) % 2 == 0)

        elementos.append({
            'tipo': 'jugador',
            'oculto': parpadeo,
            'y_sort': self.jugador['y'] + ajustes.JUG_H,
            'x': self.jugador['x'] - camara['x'],
            'y': self.jugador['y'] - camara['y'],
            'sprite': sprite,
        })

        for enemigo in self.enemigos:
            imagen = enemigo.imagen
            if not enemigo.vivo or imagen is None:
                continue
            elementos.append({
                'tipo': 'enemigo',
                'y_sort': enemigo.y_sort,
                'x': enemigo.x - camara['x'],
                'y': enemigo.y - camara['y'],
                'sprite': imagen,
                'ref': enemigo,
                # Si la criatura tiene animacion de daño propia no se suma destello
                'destello': enemigo.destella,
            })

        for npc in self.npcs:
            elementos.append({
                'tipo': 'npc',
                'y_sort': npc['y'] + ajustes.JUG_H,
                'x': npc['x'] - camara['x'],
                'y': npc['y'] - camara['y'],
                'sprite': npc['sprite'],
                'ref': npc,
            })

        # Objetos ordenados por profundidad. Todos se apoyan por su BASE en el
        # borde de abajo de su celda y se desbordan hacia arriba, como un arbol:
        # asi el jugador pasa por delante o por detras segun donde esten sus pies
        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                # Las dos capas pueden traer objetos que se ordenan por
                # profundidad: un arbol del suelo o uno puesto en DECOR
                for caracter in (self.nivel.celda(col, fil),
                                 self.nivel.adorno(col, fil)):
                    if caracter not in self.objeto_profundos:
                        continue
                    sprite = self.sprite_objeto(caracter)
                    if sprite is None:
                        continue
                    base = (fil + 1) * ajustes.TILE_H
                    elementos.append({
                        'tipo': 'tile',
                        'y_sort': base,
                        'x': col * ajustes.TILE_W + ajustes.TILE_W // 2 - sprite.get_width() // 2 - camara['x'],
                        'y': base - sprite.get_height() - camara['y'],
                        'sprite': sprite,
                        'caracter': caracter,
                        'celda': (col, fil),
                    })

        elementos.sort(key=lambda e: e['y_sort'])

        #dibujamos todo
        for e in elementos:
            if not e.get('oculto'):
                pantalla.blit(e['sprite'], (e['x'], e['y']))
                if e.get('destello'):
                    # Se suma luz sobre el sprite
                    brillo = e['sprite'].copy()
                    brillo.fill((120, 90, 90), special_flags=pygame.BLEND_RGB_ADD)
                    brillo.set_alpha(150)
                    pantalla.blit(brillo, (e['x'], e['y']))
            if ajustes.MOSTRAR_DEPURACION:
                self.dibujar_hitbox(pantalla, e)

    def dibujar_hitbox(self, pantalla, elemento):
        #Dibuja lo de depuracion si esta activa
        if not ajustes.MOSTRAR_DEPURACION:
            return
        camara = self.camera
        if elemento['tipo'] == 'jugador':
            hb = self.hitbox_pies(elemento['x'] + camara['x'], elemento['y'] + camara['y'])
            pygame.draw.rect(pantalla, ajustes.HITBOX_JUGADOR,
                             (hb.x - camara['x'], hb.y - camara['y'], hb.width, hb.height), 1)
        elif elemento['tipo'] == 'npc':
            if elemento['ref'].get('solido', False):
                hb = geometria.caja_pies_jugador(elemento['x'], elemento['y'])
                pygame.draw.rect(pantalla, ajustes.HITBOX_NPC, hb, 1)
        elif elemento['tipo'] == 'enemigo':
            hb = elemento['ref'].hitbox
            pygame.draw.rect(pantalla, (220, 90, 200),
                             (hb.x - camara['x'], hb.y - camara['y'], hb.width, hb.height), 1)
        # Las cajas de los tiles se dibujan todas juntas en dibujar_colisiones

    def dibujar_colisiones(self, pantalla, rango):
        #Marca lo que estorba de verdad en cada casilla
        if not (ajustes.MOSTRAR_DEPURACION):
            return
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                if not self.nivel.es_solido(col, fil):
                    continue
                hb = self.hitbox_tile(col, fil)
                pygame.draw.rect(pantalla, ajustes.HITBOX_TILE,
                                 (hb.x - camara['x'], hb.y - camara['y'],
                                  hb.width, hb.height), 1)

    def dibujar_rejilla(self, pantalla, rango):
        #Dibuja (columna, fila) sobre cada tile para identificarlos facil
        if not (ajustes.MOSTRAR_DEPURACION and self.estado.mostrar_rejilla):
            return
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                px = col * ajustes.TILE_W - camara['x']
                py = fil * ajustes.TILE_H - camara['y']
                pygame.draw.rect(pantalla, ajustes.COLOR_REJILLA,
                                 (px, py, ajustes.TILE_W, ajustes.TILE_H), 1)
                if (col, fil) not in self._cache_rejilla:
                    txt = self.font_rejilla.render('%d,%d' % (col, fil), True, (25, 25, 25))
                    fondo = pygame.Surface((txt.get_width() + 4, txt.get_height() + 2),
                                           pygame.SRCALPHA)
                    fondo.fill((255, 255, 255, 195))
                    fondo.blit(txt, (2, 1))
                    self._cache_rejilla[(col, fil)] = fondo
                pantalla.blit(self._cache_rejilla[(col, fil)], (px + 2, py + 2))

    def dibujar_info(self, pantalla):
        #Dibuja la info si esta activa la depuracion
        if not ajustes.MOSTRAR_DEPURACION:
            return
        jugador = self.jugador
        estado = ('ATACANDO' if jugador['atacando']
                  else ('MOVIENDOSE' if jugador['moviendose'] else 'QUIETO'))
        col, fil = self.tile_del_jugador()
        texto = ('%s  Tile: %d,%d | %s | Mapa: %dx%d | ESPACIO=atacar  G=rejilla'
                 % (self.nivel.titulo, col, fil, estado,
                    self.nivel.cols, self.nivel.filas))
        info = self.font.render(texto, True, ajustes.NEGRO)
        pygame.draw.rect(pantalla, ajustes.BLANCO,
                         (0, ajustes.ALTO - 22, ajustes.ANCHO, 22))
        pantalla.blit(info, (5, ajustes.ALTO - 18))
    #endregion
