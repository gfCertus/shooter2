"""
Capa 6: Orquestador / Bucle Principal (main)
============================================
Configura la ventana a 800 x 600 px a 60 FPS y coordina el flujo secuencial
en cada frame:

  1. Capturar comandos (LocalInputHandler).
  2. Procesar comandos en el modelo (GameState).
  3. Actualizar simulacion fisica (GameState.update()).
  4. Extraer snapshot (GameState.get_snapshot()).
  5. Dibujar escena (PygameRenderer.render(snapshot)).

Compatible con pygame tradicional y pygame-ce.
"""
import time

from compat import pygame
from domain import Player
from input_handler import LocalInputHandler
from renderer import PygameRenderer
from state import GameState


def main() -> None:
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
