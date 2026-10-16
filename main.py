"""
Punto de entrada del Shooter 2D Multijugador (red local).

Uso por línea de comandos:
    python main.py server [--port PUERTO]     # Inicia el servidor autoritativo
    python main.py client [--host IP] [--port PUERTO]  # Inicia un cliente

Sin argumentos lanza la interfaz gráfica (tkinter) para configurar servidor y cliente.
"""
import os
import sys

from server import GameServer
from client import GameClient
from common import HOST_CLIENT_DEFAULT, HOST_SERVER, PORT


def _launch_gui() -> None:
    """Lanza la interfaz gráfica de tkinter."""
    from launcher_gui import main as gui_main

    gui_main()


def main() -> None:
    exe_name = os.path.basename(sys.argv[0]).lower()

    # Si el ejecutable se llama shooter_launcher, siempre abrir la GUI
    if "launcher" in exe_name:
        _launch_gui()
        return

    # Modo por línea de comandos
    if len(sys.argv) < 2:
        # Sin argumentos: lanzar GUI por defecto
        _launch_gui()
        return

    modo = sys.argv[1].lower()

    if modo == "server":
        # Remover 'server' y pasar el resto a argparse de server.py
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        GameServer().run()
    elif modo == "client":
        # Remover 'client' y pasar el resto a argparse de client.py
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        GameClient().run()
    else:
        print(f"Modo desconocido: {modo}")
        print("Usa 'server' o 'client', o ejecuta sin argumentos para la interfaz gráfica.")
        sys.exit(1)


if __name__ == "__main__":
    main()
