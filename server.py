"""
Capa de Red: Servidor Autoritativo
==================================
Ejecuta la lógica del juego en GameState y es la única fuente de verdad.
Acepta exactamente 2 clientes (p1 y p2), recibe sus inputs y transmite
el snapshot del estado a ambos a 60 FPS.
"""
import socket
import threading
import json
import time

from common import HOST_SERVER, PORT, BUFFER_SIZE, encode, MSG_JOIN, MSG_INPUT
from state import GameState
from commands import Command
import sys


class GameServer:
    """Servidor autoritativo del shooter 2D multijugador."""

    def __init__(self, host: str = HOST_SERVER, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.state = GameState(width=800, height=600)
        # Jugadores en el borde inferior, uno a cada lado
        self.state.register_player("p1", x=150.0, y=550.0)
        self.state.register_player("p2", x=610.0, y=550.0)

        self.clients: dict = {}          # player_id -> socket
        self.input_queues: dict = {}     # player_id -> lista de comandos str
        self.lock = threading.Lock()
        self.running = False

    # ------------------------------------------------------------------
    # Comunicación con clientes
    # ------------------------------------------------------------------
    def _send(self, conn: socket.socket, msg: dict) -> None:
        try:
            conn.sendall(encode(msg))
        except OSError:
            pass

    def _handle_client(self, conn: socket.socket, addr, player_id: str) -> None:
        """Hilo que lee los inputs de un cliente específico."""
        self._send(conn, {"type": MSG_JOIN, "player_id": player_id})
        buffer = ""
        while self.running:
            try:
                data = conn.recv(BUFFER_SIZE)
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
                    if msg.get("type") == MSG_INPUT:
                        cmds = msg.get("commands", [])
                        with self.lock:
                            self.input_queues.setdefault(player_id, []).extend(cmds)
            except OSError:
                break
        # Limpieza al desconectar
        with self.lock:
            self.clients.pop(player_id, None)
            self.input_queues.pop(player_id, None)
        try:
            conn.close()
        except OSError:
            pass

    def _broadcast_snapshot(self) -> None:
        """Envía el snapshot actual a todos los clientes conectados."""
        snapshot = self.state.get_snapshot()
        msg = {"type": "snapshot", "snapshot": snapshot}
        data = encode(msg)
        for pid, conn in list(self.clients.items()):
            try:
                conn.sendall(data)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Bucle principal del servidor
    # ------------------------------------------------------------------
    def run(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(2)
        print(f"[Servidor] Escuchando en {self.host}:{self.port}", flush=True)

        self.running = True

        # Aceptar exactamente 2 clientes
        player_ids = ["p1", "p2"]
        for pid in player_ids:
            conn, addr = server.accept()
            print(f"[Servidor] Jugador {pid} conectado desde {addr}", flush=True)
            with self.lock:
                self.clients[pid] = conn
                self.input_queues[pid] = []
            t = threading.Thread(
                target=self._handle_client, args=(conn, addr, pid), daemon=True
            )
            t.start()

        print("[Servidor] ¡Dos jugadores conectados! Iniciando bucle de juego...", flush=True)
        last_time = time.time()

        try:
            while self.running:
                now = time.time()
                dt = now - last_time
                last_time = now
                current_time = now

                # Procesar inputs pendientes
                with self.lock:
                    queues = dict(self.input_queues)
                    for pid in self.input_queues:
                        self.input_queues[pid] = []

                for pid, cmds in queues.items():
                    for cmd_str in cmds:
                        try:
                            cmd = Command(cmd_str)
                            self.state.process_command(pid, cmd, current_time)
                        except ValueError:
                            continue

                self.state.update(current_time, dt)
                self._broadcast_snapshot()

                # Limitar a 60 FPS
                elapsed = time.time() - now
                target = 1.0 / 60.0
                if elapsed < target:
                    time.sleep(target - elapsed)
        except KeyboardInterrupt:
            print("\n[Servidor] Detenido por el usuario.", flush=True)
        finally:
            self.running = False
            for conn in list(self.clients.values()):
                try:
                    conn.close()
                except OSError:
                    pass
            server.close()
            print("[Servidor] Cerrado.", flush=True)


if __name__ == "__main__":
    try:
        GameServer().run()
    except Exception as e:
        print(f"\n[ERROR] El servidor falló al iniciar: {e}", flush=True)
        print("\nPresiona ENTER para cerrar...", flush=True)
        try:
            input()
        except EOFError:
            pass
        sys.exit(1)
