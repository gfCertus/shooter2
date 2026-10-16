"""
Juego Shooter 2D - Arquitectura Desacoplada (Model-View-Controller / Clean Architecture)
=======================================================================================

Implementación completa siguiendo el documento de especificacion context.md.
Compatible con `pygame` tradicional y `pygame-ce`.

Capas:
  1. Dominio y Comandos (Enum Command)
  2. Modelo del Dominio (Player, Bullet, Enemy) - Puro Python, sin pygame
  3. Estado Central (GameState)
  4. Captura de Entradas (LocalInputHandler)
  5. Renderizador (PygameRenderer)
  6. Orquestador / Bucle Principal (main)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any

# ---------------------------------------------------------------------------
# Compatibilidad pygame / pygame-ce
# ---------------------------------------------------------------------------
try:
    import pygamece as pygame  # type: ignore
except ImportError:  # pragma: no cover
    import pygame  # type: ignore


# ===========================================================================
# Capa 1: Dominio y Comandos
# ===========================================================================

class Command(Enum):
    """Acciones abstractas del dominio. Independientes de cualquier input."""
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    SHOOT = "shoot"


# ===========================================================================
# Capa 2: Modelo del Dominio (Puro Python)
# ===========================================================================
# RESTRICCIÓN CRÍTICA: estas clases no importan ni instancian objetos de pygame.
# Las colisiones se resuelven algebraicamente.

@dataclass
class Player:
    """Representa la nave del jugador."""
    player_id: str
    x: float
    y: float
    width: float = 40.0
    height: float = 30.0
    speed: float = 5.0
    last_shot: float = 0.0
    # Tiempo de recarga entre disparos (RN-01: 200 ms = 0.2 s).
    reload_time: float = 0.2


@dataclass
class Bullet:
    """Representa un proyectil vertical."""
    x: float
    y: float
    width: float = 6.0
    height: float = 14.0
    speed: float = -7.0  # Se mueve hacia arriba (y negativa)


@dataclass
class Enemy:
    """Representa un obstáculo circular."""
    x: float
    y: float
    radius: float = 16.0
    speed: float = 3.0  # Se mueve hacia abajo (y positiva)


# ===========================================================================
# Capa 3: Estado Central (GameState)
# ===========================================================================

class GameState:
    """Estado central y soberano del juego (RN-05).

    Toda modificacion de vida, puntaje, creacion o eliminacion de entidades
    reside unicamente aqui. La vista es de solo lectura.
    """

    def __init__(self, width: int = 800, height: int = 600) -> None:
        self.width: int = width
        self.height: int = height
        self.players: Dict[str, Player] = {}
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.score: int = 0

        # Temporizador de generacion de enemigos.
        self.enemy_spawn_timer: float = 0.0
        self.enemy_spawn_interval: float = 1.0  # segundos

    # ------------------------------------------------------------------
    # Procesamiento de comandos (abstracciones de Capa 1)
    # ------------------------------------------------------------------
    def process_command(self, player_id: str, command: Command, current_time: float) -> None:
        """Ejecuta la accion indicada por el comando sobre el jugador."""
        player = self.players.get(player_id)
        if player is None:
            return

        if command == Command.MOVE_LEFT:
            player.x -= player.speed
        elif command == Command.MOVE_RIGHT:
            player.x += player.speed
        elif command == Command.SHOOT:
            self._shoot(player, current_time)

        # RN-03: restringir x dentro de {ANCHO} - {ancho_nave}
        min_x = 0.0
        max_x = float(self.width) - player.width
        player.x = min(max(player.x, min_x), max_x)

    def _shoot(self, player: Player, current_time: float) -> None:
        """Dispara un proyectil respetando la cadencia maxima (RN-01)."""
        if current_time - player.last_shot >= player.reload_time:
            bullet_x = player.x + player.width / 2.0
            bullet_y = player.y
            self.bullets.append(Bullet(x=bullet_x, y=bullet_y))
            player.last_shot = current_time

    # ------------------------------------------------------------------
    # Simulacion logica en un tick
    # ------------------------------------------------------------------
    def update(self, current_time: float, dt: float) -> None:
        """Avanza la simulacion un tick: movimiento, colisiones, purgado y spawn."""
        self._move_entities()
        self._resolve_collisions()
        self._purge_entities()          # RN-04
        self._spawn_enemies(current_time, dt)

    def _move_entities(self) -> None:
        for bullet in self.bullets:
            bullet.y += bullet.speed
        for enemy in self.enemies:
            enemy.y += enemy.speed

    def _resolve_collisions(self) -> None:
        """RN-02: impacto bala-enemigo destruye ambas y otorga +10 puntos."""
        bullets_to_remove: List[int] = []
        enemies_to_remove: List[int] = []

        for bi, bullet in enumerate(self.bullets):
            for ei, enemy in enumerate(self.enemies):
                if ei in enemies_to_remove:
                    continue
                if self._rect_circle_collide(
                    bullet.x, bullet.y, bullet.width, bullet.height,
                    enemy.x, enemy.y, enemy.radius,
                ):
                    bullets_to_remove.append(bi)
                    enemies_to_remove.append(ei)
                    self.score += 10
                    break  # Una bala solo destruye un enemigo

        # Eliminar en orden inverso para no invalidar indices
        for idx in sorted(set(bullets_to_remove), reverse=True):
            self.bullets.pop(idx)
        for idx in sorted(set(enemies_to_remove), reverse=True):
            self.enemies.pop(idx)

    @staticmethod
    def _rect_circle_collide(
        rx: float, ry: float, rw: float, rh: float,
        cx: float, cy: float, radius: float,
    ) -> bool:
        """Deteccion algebraica de colision rectangulo-circulo (sin pygame)."""
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))
        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy <= radius * radius

    def _purge_entities(self) -> None:
        """RN-04: elimina proyectiles con y < 0 y enemigos con y > ALTO."""
        self.bullets = [b for b in self.bullets if b.y >= 0]
        self.enemies = [e for e in self.enemies if e.y <= self.height]

    def _spawn_enemies(self, current_time: float, dt: float) -> None:
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0.0
            import random
            enemy_x = float(random.randint(20, self.width - 20))
            self.enemies.append(Enemy(x=enemy_x, y=0.0))

    # ------------------------------------------------------------------
    # Snapshot (DTO / JSON-like, solo tipos nativos)
    # ------------------------------------------------------------------
    def get_snapshot(self) -> Dict[str, Any]:
        """Devuelve una representacion plana del estado actual (solo lectura)."""
        return {
            "width": self.width,
            "height": self.height,
            "score": self.score,
            "players": [
                {
                    "player_id": p.player_id,
                    "x": p.x,
                    "y": p.y,
                    "width": p.width,
                    "height": p.height,
                }
                for p in self.players.values()
            ],
            "bullets": [
                {"x": b.x, "y": b.y, "width": b.width, "height": b.height}
                for b in self.bullets
            ],
            "enemies": [
                {"x": e.x, "y": e.y, "radius": e.radius}
                for e in self.enemies
            ],
        }


# ===========================================================================
# Capa 4: Captura de Entradas (LocalInputHandler)
# ===========================================================================

class LocalInputHandler:
    """Lee el teclado local y mapea teclas a enum Command."""

    def __init__(self, player_id: str) -> None:
        self.player_id = player_id

    def get_commands(self) -> List[Command]:
        """Devuelve la lista de comandos activos en este frame."""
        keys = pygame.key.get_pressed()
        commands: List[Command] = []

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            commands.append(Command.MOVE_LEFT)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            commands.append(Command.MOVE_RIGHT)
        if keys[pygame.K_SPACE]:
            commands.append(Command.SHOOT)

        return commands


# ===========================================================================
# Capa 5: Renderizador (PygameRenderer)
# ===========================================================================

class PygameRenderer:
    """Dibuja exclusivamente a partir del snapshot de GameState."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)

    def render(self, snapshot: Dict[str, Any]) -> None:
        """Limpia pantalla y dibuja jugadores, balas, enemigos y puntaje."""
        self.screen.fill((0, 0, 0))

        # Jugadores como rectangulos verdes
        for p in snapshot["players"]:
            pygame.draw.rect(
                self.screen,
                (0, 255, 0),
                (int(p["x"]), int(p["y"]), int(p["width"]), int(p["height"])),
            )

        # Proyectiles como rectangulos amarillos
        for b in snapshot["bullets"]:
            pygame.draw.rect(
                self.screen,
                (255, 255, 0),
                (int(b["x"]), int(b["y"]), int(b["width"]), int(b["height"])),
            )

        # Enemigos como circulos rojos
        for e in snapshot["enemies"]:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (int(e["x"]), int(e["y"])),
                int(e["radius"]),
            )

        # Puntaje en la esquina superior izquierda
        score_text = self.font.render(
            f"Score: {snapshot['score']}", True, (255, 255, 255)
        )
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()


# ===========================================================================
# Capa 6: Orquestador / Bucle Principal (main)
# ===========================================================================

def main() -> None:
    """Configura ventana, coordina el flujo secuencial por frame."""
    pygame.init()

    ANCHO: int = 800
    ALTO: int = 600
    FPS: int = 60

    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Shooter 2D - Arquitectura Limpia")
    clock = pygame.time.Clock()

    # Inicializar estado y componentes
    state = GameState(width=ANCHO, height=ALTO)
    state.players["p1"] = Player(player_id="p1", x=ANCHO / 2 - 20, y=ALTO - 50)

    input_handler = LocalInputHandler(player_id="p1")
    renderer = PygameRenderer(screen=screen)

    running = True
    while running:
        # Eventos del sistema (salida)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()
        dt = clock.tick(FPS) / 1000.0  # segundos transcurridos en este frame

        # 1. Capturar comandos
        commands = input_handler.get_commands()

        # 2. Procesar comandos en el modelo
        for cmd in commands:
            state.process_command("p1", cmd, current_time)

        # 3. Actualizar simulacion fisica
        state.update(current_time, dt)

        # 4. Extraer snapshot
        snapshot = state.get_snapshot()

        # 5. Dibujar escena
        renderer.render(snapshot)

    pygame.quit()


if __name__ == "__main__":
    main()
