"""
Punto de entrada del Shooter 2D Multijugador (red local).

Uso:
    python main.py server          # Inicia el servidor autoritativo
    python main.py client [host]   # Inicia un cliente (host opcional, default localhost)
"""
import sys

from server import GameServer
from client import GameClient
from common import HOST_SERVER, HOST_CLIENT_DEFAULT


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python main.py server          # Inicia el servidor autoritativo")
        print("  python main.py client [host]   # Inicia un cliente")
        sys.exit(1)

    modo = sys.argv[1].lower()

    if modo == "server":
        GameServer().run()
    elif modo == "client":
        host = sys.argv[2] if len(sys.argv) > 2 else HOST_CLIENT_DEFAULT
        GameClient(host=host).run()
    else:
        print(f"Modo desconocido: {modo}")
        print("Usa 'server' o 'client'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
