"""
Capa 4: Captura de Entradas (LocalInputHandler)
===============================================
Lee eventos de teclado mediante pygame.key.get_pressed() y mapea teclas
locales a una lista de enum Command. Cada jugador puede tener su propio
mapa de teclas.
"""
from typing import List, Dict

from compat import pygame
from commands import Command


class LocalInputHandler:
    """Lee el teclado local y mapea teclas a enum Command."""

    DEFAULT_KEYMAP = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "shoot": pygame.K_SPACE,
        "alt_left": pygame.K_a,
        "alt_right": pygame.K_d,
    }

    def __init__(self, player_id: str, keymap: Dict[str, int] = None) -> None:
        self.player_id = player_id
        self.keymap = keymap or self.DEFAULT_KEYMAP

    def get_commands(self) -> List[Command]:
        """Devuelve la lista de comandos activos en este frame."""
        keys = pygame.key.get_pressed()
        commands: List[Command] = []

        if keys[self.keymap["left"]] or keys[self.keymap["alt_left"]]:
            commands.append(Command.MOVE_LEFT)
        if keys[self.keymap["right"]] or keys[self.keymap["alt_right"]]:
            commands.append(Command.MOVE_RIGHT)
        if keys[self.keymap["shoot"]]:
            commands.append(Command.SHOOT)

        return commands
