"""
Capa 1: Dominio y Comandos
==========================
Define las acciones abstractas del juego. Son independientes de cualquier
teclado, ratón o red; solo representan la intención del jugador.
"""
from enum import Enum


class Command(Enum):
    """Acciones abstractas del dominio."""
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    SHOOT = "shoot"
