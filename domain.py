"""
Capa 2: Modelo del Dominio (Puro Python)
========================================
Player, Bullet y Enemy. RESTRICCIÓN CRÍTICA: estas clases no importan ni
instancian objetos de pygame. Las colisiones se resuelven algebraicamente
desde GameState, no aquí.

Ahora Bullet conoce a su dueño (player_id) para asignar puntajes
individuales en el modo multijugador.
"""
from dataclasses import dataclass


@dataclass
class Player:
    """Representa la nave de un jugador."""
    player_id: str
    x: float
    y: float
    width: float = 40.0
    height: float = 30.0
    speed: float = 5.0
    last_shot: float = 0.0
    # RN-01: tiempo de recarga entre disparos (200 ms = 0.2 s).
    reload_time: float = 0.2


@dataclass
class Bullet:
    """Representa un proyectil vertical."""
    x: float
    y: float
    player_id: str  # Jugador que disparó este proyectil (para puntaje individual)
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
