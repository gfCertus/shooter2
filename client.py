"""
Capa de Red: Cliente
====================
Se conecta al servidor autoritativo, captura los inputs locales y los envía.
Recibe snapshots del servidor y los renderiza en pantalla local.
"""
import socket
import threading
import json
import time

import pygame

from common import HOST_CLIENT_DEFAULT, PORT, BUFFER_SIZE, MSG_JOIN, MSG_INPUT, MSG_SNAPSHOT
from input_handler import LocalInputHandler
from renderer import PygameRenderer


class GameClient:
    """Cliente del shooter 2D multijugador."""

    def __init__(self, host: str = HOST_CLIENT_DEFAULT) -> None:
        self.host = host
        self.sock: socket.socket = None
        self.player_id: str = None
        self.snapshot: dict = None
        self.lock = threading.Lock()
        self.running = False

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, PORT))
        print(f"[Cliente] Conectado a {self.host}:{PORT}")

        # Leer mensaje de bienvenida para saber nuestro player_id
        buffer = ""
        while self.player_id is None:
            data = self.sock.recv(BUFFER_SIZE)
            if not data:
                raise ConnectionError("Servidor cerró la conexión")
            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if msg.get("type") == MSG_JOIN:
                    self.player_id = msg["player_id"]
                    print(f"[Cliente] Eres el jugador {self.player_id}")
                    break

    def _receive_loop(self) -> None:
        """Hilo que recibe snapshots del servidor."""
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if msg.get("type") == MSG_SNAPSHOT:
                        with self.lock:
                            self.snapshot = msg.get("snapshot")
            except OSError:
                break

    def _send_input(self, commands: list) -> None:
        if not commands:
            return
        msg = {"type": MSG_INPUT, "commands": commands}
        try:
            self.sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        except OSError:
            pass

    def run(self) -> None:
        self.connect()
        self.running = True

        # Hilo de recepción de snapshots
        recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        recv_thread.start()

        # Configuración de pygame local
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(f"Shooter 2D Multijugador - Jugador {self.player_id}")
        clock = pygame.time.Clock()

        # Teclas según jugador
        if self.player_id == "p1":
            keymap = {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "shoot": pygame.K_SPACE,
                "alt_left": pygame.K_a,
                "alt_right": pygame.K_d,
            }
        else:
            keymap = {
                "left": pygame.K_a,
                "right": pygame.K_d,
                "shoot": pygame.K_LSHIFT,
                "alt_left": pygame.K_LEFT,
                "alt_right": pygame.K_RIGHT,
            }

        input_handler = LocalInputHandler(player_id=self.player_id, keymap=keymap)
        renderer = PygameRenderer(screen=screen)

        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                # Capturar inputs locales y enviarlos al servidor
                commands = input_handler.get_commands()
                self._send_input(commands)

                # Renderizar el último snapshot recibido
                with self.lock:
                    snap = self.snapshot
                if snap is not None:
                    renderer.render(snap)

                clock.tick(60)
        finally:
            self.running = False
            try:
                self.sock.close()
            except OSError:
                pass
            pygame.quit()
            print("[Cliente] Desconectado.")


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    GameClient(host=host).run()
