"""
Compatibilidad entre pygame tradicional y pygame-ce.
Permite que el proyecto funcione con cualquiera de las dos librerias sin
cambiar el resto del codigo.
"""
try:
    import pygamece as pygame  # type: ignore
except ImportError:  # pragma: no cover
    import pygame  # type: ignore

__all__ = ["pygame"]
