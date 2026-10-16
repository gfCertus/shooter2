"""
Capa 5: Renderizador (PygameRenderer)
======================================
Recibe exclusivamente el diccionario generado por GameState.get_snapshot().
Limpia la pantalla y dibuja:
  * Jugadores como rectángulos (p1 verde, p2 cian).
  * Proyectiles como rectángulos amarillos.
  * Enemigos como círculos rojos.
  * Puntaje individual de cada jugador (esquina izquierda y derecha).
"""
from typing import Any, Dict

from compat import pygame


class PygameRenderer:
    """Dibuja exclusivamente a partir del snapshot de GameState."""

    COLORES_JUGADOR = {
        "p1": (0, 255, 0),    # Verde
        "p2": (0, 200, 255),  # Cian
    }

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)

    def render(self, snapshot: Dict[str, Any]) -> None:
        """Limpia pantalla y dibuja jugadores, balas, enemigos y puntajes."""
        self.screen.fill((0, 0, 0))

        # Jugadores como rectángulos (color según jugador)
        for p in snapshot["players"]:
            color = self.COLORES_JUGADOR.get(p["player_id"], (255, 255, 255))
            pygame.draw.rect(
                self.screen,
                color,
                (int(p["x"]), int(p["y"]), int(p["width"]), int(p["height"])),
            )

        # Proyectiles como rectángulos amarillos
        for b in snapshot["bullets"]:
            pygame.draw.rect(
                self.screen,
                (255, 255, 0),
                (int(b["x"]), int(b["y"]), int(b["width"]), int(b["height"])),
            )

        # Enemigos como círculos rojos
        for e in snapshot["enemies"]:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (int(e["x"]), int(e["y"])),
                int(e["radius"]),
            )

        # Puntajes individuales: p1 esquina izquierda, p2 esquina derecha
        scores = snapshot.get("scores", {})
        score_p1 = scores.get("p1", 0)
        score_p2 = scores.get("p2", 0)

        text_p1 = self.font.render(f"P1: {score_p1}", True, (0, 255, 0))
        text_p2 = self.font.render(f"P2: {score_p2}", True, (0, 200, 255))

        self.screen.blit(text_p1, (10, 10))
        self.screen.blit(text_p2, (snapshot["width"] - text_p2.get_width() - 10, 10))

        pygame.display.flip()
