"""
Capa 3: Estado Central (GameState)
===================================
Mantiene el estado soberano del juego (RN-05). Toda modificacion de vida,
puntaje, creacion o eliminacion de entidades reside unicamente aqui. La vista
es de solo lectura.

No importa pygame: trabaja con tipos nativos y las clases de dominio.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List

from commands import Command
from domain import Bullet, Enemy, Player


class GameState:
    """Estado central y soberano del juego."""

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

    def _spawn_enemies(self, _current_time: float, dt: float) -> None:
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0.0
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
