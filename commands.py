"""
Capa 1: Dominio y Comandos
==========================
Define las acciones abstractas del juego. Son independientes de cualquier
teclado, raton o red; solo representan la intencion del jugador.
"""
from enum import Enum


class Command(Enum):
    """Acciones abstractas del dominio."""
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    SHOOT = "shoot"
