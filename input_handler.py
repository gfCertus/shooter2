"""
Capa 4: Captura de Entradas (LocalInputHandler)
===============================================
Lee eventos de teclado mediante pygame.key.get_pressed() y mapea teclas
locales a una lista de enum Command.
"""
from typing import List

from compat import pygame
from commands import Command


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
