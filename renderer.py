"""
Capa 5: Renderizador (PygameRenderer)
======================================
Recibe exclusivamente el diccionario generado por GameState.get_snapshot().
Limpia la pantalla y dibuja:
  * Jugadores como rectangulos verdes.
  * Proyectiles como rectangulos amarillos.
  * Enemigos como circulos rojos.
  * Puntaje en la esquina superior izquierda usando pygame.font.
"""
from typing import Any, Dict

from compat import pygame


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
